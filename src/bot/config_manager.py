import json
import shutil
from pathlib import Path
from typing import Literal

CONFIG_DIR = Path(__file__).parent.parent / "config"
TEMPLATE_PATH = CONFIG_DIR / "config_template.json"


# ---------------------------------------------------------------------------
# Data classes (carried over from v2 rework)
# ---------------------------------------------------------------------------


class CustomCommand:
    """Holds all metadata for a single command."""

    def __init__(
        self,
        command: str,
        response: str | None,
        /,
        cmd_type: str = "simple",
        enabled: bool = True,
        user_cooldown: int = 0,
        global_cooldown: int = 0,
        restriction: Literal["streamer", "mod", "vip", "sub", "none"] = "none",
        display_name: str | None = None,
        description: str | None = None,
    ):
        self.command = command
        self.response = response
        self.cmd_type = cmd_type
        self.enabled = enabled
        self.user_cooldown = user_cooldown
        self.global_cooldown = global_cooldown
        self.restriction = restriction
        self.display_name = display_name or command
        self.description = description or ""

    def to_dict(self) -> dict:
        return {
            "type": self.cmd_type,
            "enabled": self.enabled,
            "response": self.response,
            "userCooldown": self.user_cooldown,
            "globalCooldown": self.global_cooldown,
            "restriction": self.restriction,
            "displayName": self.display_name,
            "description": self.description,
        }

    @classmethod
    def from_dict(cls, name: str, data: dict) -> "CustomCommand":
        return cls(
            name,
            data.get("response"),
            cmd_type=data.get("type", "simple"),
            enabled=data.get("enabled", True),
            user_cooldown=data.get("userCooldown", 0),
            global_cooldown=data.get("globalCooldown", 0),
            restriction=data.get("restriction", "none"),
            display_name=data.get("displayName"),
            description=data.get("description"),
        )


class CustomResponseHelper:
    """Replaces placeholders in command response templates."""

    @staticmethod
    def replace(
        response: str,
        *,
        user: str | None = None,
        target: str | None = None,
        streamer: str | None = None,
        counter: int | None = None,
    ) -> str:
        result = response
        if user is not None:
            result = result.replace("{username}", str(user))
        if target is not None:
            result = result.replace("{target}", str(target))
        if streamer is not None:
            result = result.replace("{streamer}", str(streamer))
        if counter is not None:
            result = result.replace("{counter}", str(counter))
        return result


class Queue:
    """Manages a player queue for viewer games / giveaways."""

    def __init__(self, players: list, multi_join: bool, joinable: bool):
        self.players: list = players
        self.multi_join: bool = multi_join
        self.joinable: bool = joinable

    def add_player(self, player: str) -> None:
        self.players.append(player)

    def remove_player(self, player: str) -> None:
        if player in self.players:
            self.players.remove(player)

    def remove_all_instances(self, player: str) -> None:
        self.players = [p for p in self.players if p.lower() != player.lower()]

    def to_dict(self) -> dict:
        return {
            "players": self.players,
            "multiJoin": self.multi_join,
            "joinable": self.joinable,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Queue":
        return cls(
            players=data.get("players", []),
            multi_join=data.get("multiJoin", True),
            joinable=data.get("joinable", False),
        )


# ---------------------------------------------------------------------------
# Config load / save
# ---------------------------------------------------------------------------


def load_config(file_path: str | Path) -> dict:
    """Load JSON config. Creates from template if missing."""
    file_path = Path(file_path)
    try:
        with open(file_path, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Config not found. Creating from template: {file_path}")
        create_default_config(file_path)
        return load_config(file_path)
    except json.JSONDecodeError as e:
        print(f"Invalid JSON in config: {e}")
        return {}


def save_config(file_path: str | Path, config: dict) -> None:
    """Write config dict to JSON file."""
    file_path = Path(file_path)
    file_path.parent.mkdir(parents=True, exist_ok=True)
    with open(file_path, "w") as f:
        json.dump(config, f, indent=4)


def create_default_config(file_path: str | Path) -> None:
    """Copy template to create a new config file."""
    file_path = Path(file_path)
    file_path.parent.mkdir(parents=True, exist_ok=True)
    if TEMPLATE_PATH.exists():
        shutil.copy(TEMPLATE_PATH, file_path)
    else:
        save_config(
            file_path, {"userSettings": {}, "commands": {}, "counters": {}, "lists": {}}
        )


def update_config(file_path: str | Path, key_path: list, value) -> dict:
    """Update a nested config value by key path. Returns updated config."""
    config = load_config(file_path)
    current = config
    for key in key_path[:-1]:
        if key not in current or not isinstance(current[key], dict):
            current[key] = {}
        current = current[key]
    current[key_path[-1]] = value
    save_config(file_path, config)
    return config


# ---------------------------------------------------------------------------
# Config readers
# ---------------------------------------------------------------------------


def get_enabled_commands(config: dict) -> dict[str, CustomCommand]:
    """Return dict of enabled CustomCommand objects from config."""
    commands = config.get("commands", {})
    return {
        name: CustomCommand.from_dict(name, data)
        for name, data in commands.items()
        if data.get("enabled", True)
    }


def get_counters(config: dict) -> dict[str, int]:
    """Return dict of counter_name -> current_value."""
    counters = config.get("counters", {})
    return {name: data.get("counter", 0) for name, data in counters.items()}


def get_queue(config: dict) -> Queue:
    """Return Queue object from config."""
    queue_data = config.get("lists", {}).get("queue", {})
    return Queue.from_dict(queue_data)
