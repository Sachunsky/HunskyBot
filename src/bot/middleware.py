from typing import Callable, Optional, Awaitable

from twitchAPI.chat import ChatCommand
from twitchAPI.chat.middleware import BaseCommandMiddleware


class ModerationOnly(BaseCommandMiddleware):
    """Restricts command execution to moderators or the streamer."""

    def __init__(
        self,
        channel: str,
        execute_blocked_handler: Optional[Callable[[ChatCommand], Awaitable[None]]] = None,
    ):
        self.channel = channel
        self.execute_blocked_handler = execute_blocked_handler

    async def can_execute(self, cmd: ChatCommand) -> bool:
        return cmd.user.mod or cmd.user.name == self.channel

    async def was_executed(self, cmd: ChatCommand) -> None:
        pass


class VIPsOnly(BaseCommandMiddleware):
    """Restricts command execution to VIPs, mods, or the streamer."""

    def __init__(
        self,
        channel: str,
        execute_blocked_handler: Optional[Callable[[ChatCommand], Awaitable[None]]] = None,
    ):
        self.channel = channel
        self.execute_blocked_handler = execute_blocked_handler

    async def can_execute(self, cmd: ChatCommand) -> bool:
        return cmd.user.vip or cmd.user.mod or cmd.user.name == self.channel

    async def was_executed(self, cmd: ChatCommand) -> None:
        pass


class SubsOnly(BaseCommandMiddleware):
    """Restricts command execution to subscribers, VIPs, mods, or the streamer."""

    def __init__(
        self,
        channel: str,
        execute_blocked_handler: Optional[Callable[[ChatCommand], Awaitable[None]]] = None,
    ):
        self.channel = channel
        self.execute_blocked_handler = execute_blocked_handler

    async def can_execute(self, cmd: ChatCommand) -> bool:
        return (
            cmd.user.subscriber
            or cmd.user.vip
            or cmd.user.mod
            or cmd.user.name == self.channel
        )

    async def was_executed(self, cmd: ChatCommand) -> None:
        pass


class StreamerOnly(BaseCommandMiddleware):
    """Restricts command execution to the streamer only."""

    def __init__(
        self,
        channel: str,
        execute_blocked_handler: Optional[Callable[[ChatCommand], Awaitable[None]]] = None,
    ):
        self.channel = channel
        self.execute_blocked_handler = execute_blocked_handler

    async def can_execute(self, cmd: ChatCommand) -> bool:
        return cmd.user.name == self.channel

    async def was_executed(self, cmd: ChatCommand) -> None:
        pass


# Map restriction strings from config to middleware classes
RESTRICTION_MAP = {
    "streamer": StreamerOnly,
    "mod": ModerationOnly,
    "vip": VIPsOnly,
    "sub": SubsOnly,
    "none": None,
}
