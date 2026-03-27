import asyncio
import random
import threading
from pathlib import Path

from PySide6.QtCore import QObject, Signal
from twitchAPI.chat import Chat, ChatCommand, ChatMessage, EventData
from twitchAPI.oauth import UserAuthenticator
from twitchAPI.twitch import Twitch
from twitchAPI.type import AuthScope, ChatEvent

from bot.config_manager import (
    CustomCommand,
    CustomResponseHelper,
    Queue,
    get_counters,
    get_enabled_commands,
    get_queue,
    load_config,
    save_config,
    update_config,
)
from bot.middleware import RESTRICTION_MAP

USER_SCOPES = [
    AuthScope.CHAT_READ,
    AuthScope.CHAT_EDIT,
    AuthScope.CHANNEL_MANAGE_BROADCAST,
]


class BotSignals(QObject):
    """Qt signals emitted by the bot for the GUI to consume."""

    connected = Signal()
    disconnected = Signal()
    message_received = Signal(str, str)  # (username, message)
    error = Signal(str)
    log = Signal(str)


class TwitchBot:
    """Twitch chatbot that runs in its own thread."""

    def __init__(
        self,
        app_id: str,
        secret: str,
        token: str,
        refresh_token: str,
        channel: str,
        config_path: str | Path,
    ):
        self.app_id = app_id
        self.secret = secret
        self.token = token
        self.refresh_token = refresh_token
        self.channel = channel.lower()
        self.config_path = Path(config_path)

        self.signals = BotSignals()
        self._thread: threading.Thread | None = None
        self._loop: asyncio.AbstractEventLoop | None = None
        self._chat: Chat | None = None
        self._twitch: Twitch | None = None

        # Runtime state
        self._counters: dict[str, int] = {}
        self._queue: Queue | None = None

    # --- Lifecycle ---

    def start(self) -> None:
        """Start the bot in a background thread."""
        if self._thread and self._thread.is_alive():
            self.signals.log.emit("Bot is already running.")
            return

        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        """Stop the bot gracefully."""
        if self._loop and self._loop.is_running():
            asyncio.run_coroutine_threadsafe(self._shutdown(), self._loop)

    async def _shutdown(self) -> None:
        try:
            if self._chat:
                self._chat.stop()
            if self._twitch:
                await self._twitch.close()
        except Exception as e:
            self.signals.error.emit(f"Error during shutdown: {e}")
        finally:
            self.signals.disconnected.emit()
            self.signals.log.emit("Bot stopped.")

    def _run(self) -> None:
        self._loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._loop)
        try:
            self._loop.run_until_complete(self._start_bot())
        except Exception as e:
            self.signals.error.emit(str(e))
        finally:
            self._loop.close()

    # --- Bot setup ---

    async def _start_bot(self) -> None:
        try:
            self._twitch = await Twitch(self.app_id, self.secret)
            await self._twitch.set_user_authentication(
                self.token, USER_SCOPES, self.refresh_token
            )

            self._chat = await Chat(self._twitch)

            # Load runtime state from config
            config = load_config(self.config_path)
            self._counters = get_counters(config)
            self._queue = get_queue(config)

            # Register events
            self._chat.register_event(ChatEvent.READY, self._on_connect)
            self._chat.register_event(ChatEvent.MESSAGE, self._on_message)

            # Register commands
            self._register_commands(config)

            self._chat.start()
            self.signals.log.emit("Bot starting...")

            while self._chat.is_running():
                await asyncio.sleep(1)

        except Exception as e:
            self.signals.error.emit(f"Bot error: {e}")

    def _register_commands(self, config: dict) -> None:
        """Load enabled commands from config and register them."""
        commands = get_enabled_commands(config)

        for name, cmd in commands.items():
            handler = None

            if cmd.cmd_type == "builtin":
                handler = self._get_builtin_handler(name)
                if not handler:
                    self.signals.log.emit(f"No builtin handler for: !{name}")
                    continue

            elif cmd.cmd_type == "simple" and cmd.response:
                handler = self._make_simple_handler(cmd)

            elif cmd.cmd_type == "counter":
                handler = self._make_counter_handler(name, cmd)

            if handler:
                # Get middleware for this command's restriction level
                middleware = self._get_middleware(cmd.restriction)
                if middleware:
                    self._chat.register_command(
                        name, handler, command_middleware=[middleware]
                    )
                    self.signals.log.emit(
                        f"Registered {cmd.cmd_type}: !{name} [{cmd.restriction}]"
                    )
                else:
                    self._chat.register_command(name, handler)
                    self.signals.log.emit(f"Registered {cmd.cmd_type}: !{name}")

    def _get_middleware(self, restriction: str):
        """Return a middleware instance for the given restriction, or None."""
        middleware_cls = RESTRICTION_MAP.get(restriction)
        if middleware_cls:
            return middleware_cls(self.channel)
        return None

    def _get_builtin_handler(self, name: str):
        """Map builtin command names to handler methods."""
        builtins = {
            "help": self._cmd_help,
            "lurk": self._cmd_lurk,
            "queue": self._cmd_queue,
        }
        return builtins.get(name)

    # --- Dynamic command handlers ---

    def _make_simple_handler(self, cmd: CustomCommand):
        """Create a handler for simple response commands with placeholder support."""

        async def handler(chat_cmd: ChatCommand) -> None:
            # Extract first parameter as target (e.g. for !so @username)
            param = chat_cmd.parameter.strip() if chat_cmd.parameter else ""
            target = param.split()[0].lstrip("@") if param else ""

            response = CustomResponseHelper.replace(
                cmd.response,
                user=chat_cmd.user.name,
                target=target,
                streamer=self.channel,
            )
            await chat_cmd.chat.send_message(f"#{self.channel}", response)

        return handler

    def _make_counter_handler(self, name: str, cmd: CustomCommand):
        """Create a handler for counter commands."""

        async def handler(chat_cmd: ChatCommand) -> None:
            # Increment counter
            self._counters[name] = self._counters.get(name, 0) + 1
            count = self._counters[name]

            # Persist to config
            update_config(
                self.config_path,
                ["counters", name, "counter"],
                count,
            )

            # Send response with counter placeholder
            if cmd.response:
                response = CustomResponseHelper.replace(
                    cmd.response,
                    user=chat_cmd.user.name,
                    streamer=self.channel,
                    counter=count,
                )
                await chat_cmd.chat.send_message(f"#{self.channel}", response)

        return handler

    # --- Events ---

    async def _on_connect(self, event: EventData) -> None:
        await event.chat.join_room(self.channel)
        self.signals.connected.emit()
        self.signals.log.emit(f"Connected to #{self.channel}")

    async def _on_message(self, msg: ChatMessage) -> None:
        self.signals.message_received.emit(msg.user.display_name, msg.text)

    # --- Builtin commands ---

    async def _cmd_help(self, cmd: ChatCommand) -> None:
        config = load_config(self.config_path)
        commands = get_enabled_commands(config)
        cmd_list = ", ".join(f"!{name}" for name in commands)
        await cmd.chat.send_message(f"#{self.channel}", f"Enabled commands: {cmd_list}")

    async def _cmd_lurk(self, cmd: ChatCommand) -> None:
        responses = [
            f"@{cmd.user.name} verschwindet in's Gebüsch... Möge der Lurk mit dir sein! catLurk",
            f"@{cmd.user.name} hat den Tarnmodus aktiviert. Danke fürs Lurken! PETTHECHAT",
            f"@{cmd.user.name} ist AFK gegangen, aber XP fürs Lurken gibt's trotzdem! GoodGame",
            f"@{cmd.user.name} hat den Chat in den Hintergrundprozess verschoben. CPU: 0%, Support: 100%! robotD",
        ]
        await cmd.chat.send_message(f"#{self.channel}", random.choice(responses))

    async def _cmd_queue(self, cmd: ChatCommand) -> None:
        """Full queue system: !queue, !queue open/close/join/leave/next/remove/multi"""
        if not self._queue:
            return

        text = cmd.parameter.strip() if cmd.parameter else ""
        is_privileged = cmd.user.mod or cmd.user.name == self.channel

        # !queue (no subcommand) — show the queue
        if not text:
            if not self._queue.players:
                await cmd.chat.send_message(f"#{self.channel}", "Die Queue ist leer!")
                return
            listing = " - ".join(
                f"#{i + 1}: @{p}" for i, p in enumerate(self._queue.players)
            )
            await cmd.chat.send_message(f"#{self.channel}", f"Queue: {listing}")
            return

        parts = text.split(maxsplit=1)
        sub = parts[0].lower()

        if sub == "open" and is_privileged:
            self._queue.joinable = True
            update_config(self.config_path, ["lists", "queue", "joinable"], True)
            await cmd.chat.send_message(
                f"#{self.channel}",
                'Die Queue ist nun geöffnet! "!queue join" zum Beitreten, "!queue leave" zum Verlassen.',
            )

        elif sub == "close" and is_privileged:
            self._queue.joinable = False
            update_config(self.config_path, ["lists", "queue", "joinable"], False)
            await cmd.chat.send_message(
                f"#{self.channel}", "Die Queue ist nun geschlossen!"
            )

        elif sub == "multi" and is_privileged:
            self._queue.multi_join = not self._queue.multi_join
            update_config(
                self.config_path,
                ["lists", "queue", "multiJoin"],
                self._queue.multi_join,
            )
            state = "aktiviert" if self._queue.multi_join else "deaktiviert"
            await cmd.chat.send_message(
                f"#{self.channel}", f"Multi-Join ist nun {state}!"
            )

        elif sub == "next" and is_privileged:
            if self._queue.players:
                next_player = self._queue.players.pop(0)
                await cmd.chat.send_message(
                    f"#{self.channel}", f"Nächster Spieler: @{next_player}"
                )
            else:
                await cmd.chat.send_message(
                    f"#{self.channel}", "Die Queue ist leer! D:"
                )

        elif sub == "remove" and is_privileged:
            if len(parts) > 1:
                target = parts[1].lstrip("@")
                self._queue.remove_all_instances(target)
                await cmd.chat.send_message(
                    f"#{self.channel}", f"@{target} wurde aus der Queue entfernt!"
                )
            else:
                await cmd.chat.send_message(
                    f"#{self.channel}", "Bitte gib einen Nutzernamen an."
                )

        elif sub == "join":
            if not self._queue.joinable:
                await cmd.chat.send_message(
                    f"#{self.channel}", "Die Queue ist momentan geschlossen!"
                )
            elif not self._queue.multi_join and cmd.user.name in self._queue.players:
                await cmd.chat.send_message(
                    f"#{self.channel}", f"@{cmd.user.name} ist bereits in der Queue!"
                )
            else:
                self._queue.add_player(cmd.user.name)
                await cmd.chat.send_message(
                    f"#{self.channel}", f"@{cmd.user.name} ist der Queue beigetreten!"
                )

        elif sub == "leave":
            self._queue.remove_player(cmd.user.name)
            await cmd.chat.send_message(
                f"#{self.channel}", f"@{cmd.user.name} hat die Queue verlassen!"
            )

        elif not is_privileged and sub in ("open", "close", "multi", "next", "remove"):
            await cmd.chat.send_message(
                f"#{self.channel}", f"Nix da @{cmd.user.name}. Du bist kein Moderator!"
            )
