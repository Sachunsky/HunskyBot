# Twitch API Imports
from twitchAPI.chat import Chat, EventData, ChatMessage, ChatSub, ChatCommand
from twitchAPI.type import AuthScope, ChatEvent, ChatRoom
from twitchAPI.oauth import UserAuthenticator
from twitchAPI.twitch import Twitch

# Misc
import os, json, asyncio, random
from dotenv import find_dotenv, load_dotenv
from enum import Enum
from typing import Literal

# Loading .env file
envPath = find_dotenv()
load_dotenv(envPath)

# Load Environment Variables
CONFIG_PATH = os.getenv('CONFIG_PATH')
CONFIG_TEMPLATE_PATH = os.getenv('CONFIG_TEMPLATE_PATH')
CHANNEL = os.getenv('CHANNEL')



# GOTO - Class Definitions

# Class | CustomResponseHelper
class CustomResponseHelper:
    """A helper class for managing custom responses.
    """
    def ReplaceResponsePlaceholders(response: str, *, user: str = None, streamer: str = None, counter: int = None):
        compiledResponse = response
        
        if user is not None:
            compiledResponse = compiledResponse.replace("{username}", str(user))
            
        if streamer is not None:
            compiledResponse = compiledResponse.replace("{streamer}", str(streamer))
            
        if counter is not None:
            compiledResponse = compiledResponse.replace("{counter}", str(counter))
                
        return compiledResponse


# Class | CustomCommand
class CustomCommand: 
    """Creates an object for holding Custom Command data.
    """
    
    def __init__(self, command: str, response: str, /, enabled: bool = True, userCooldown: int = 0, globalCooldown: int = 0, restriction: Literal["streamer", "mod", "vip", "sub", "none"] = "none", displayName: str = None, description: str = None):
        """Initializes the CustomCommand object with the given parameters.

        Args:
            command (str): The command handle
            response (str): The response to the command
            enabled (bool, optional): Indicates if the command is enabled in the users settings. Defaults to True.
            userCooldown (int, optional): The time a user has to wait until he can use the command again (Streamer & Mods are excluded). Defaults to 0.
            globalCooldown (int, optional): The time the community has to wait until the command can be used again by any user (Streamer & Mods are excluded). Defaults to 0.
            restriction (Literal["streamer", "mod", "vip", "sub", "none"], optional): The type of restriction placed on the command. Defaults to "none".
            displayName (str, optional): The name of the command display in the frontend. Defaults to None.
            description (str, optional): The command description displayed in the frontend. Defaults to None.
        """
        self.command: str = command
        self.response: str = response
        self.enabled: bool = enabled
        self.userCooldown: int = userCooldown
        self.globalCooldown: int = globalCooldown
        self.restriction: str = restriction
        self.displayName: str = displayName
        self.description: str = description
        

# Class | Queue
class Queue: 
    """
    Creates an object for holding Player Queue data.

    Args:
        players (array/list): the array object containing the players in the Queue.

        multiJoin (bool): the boolean object containing the multiJoin status of the Queue.

        joinable (bool): the boolean object containing the joinable status of the Queue.
    """
    
    def __init__(self, players, multiJoin, joinable):
        self.players: list = players
        self.multiJoin: bool = multiJoin
        self.joinable: bool = joinable

    def addPlayer(self, player):
        self.players.append(player)

    def removePlayer(self, player):
        self.players.remove(player)

    def setMultiJoin(self, multiJoin):
        self.multiJoin = multiJoin

    def setJoinable(self, joinable):
        self.joinable = joinable

    def removePlayerAllInstances(self, removedPlayer):
        for index in range(len(self.players)):
                if self.players[index] == removedPlayer.lower():
                    self.players.pop(index)


# Class | Config
class Config:
    """
    Creates an object for holding Config data.

    Args:
        config (dict): the dictionary object containing the loaded JSON Config.
    """
    
    # Initialize the Config object  
    def __init__(self, config: dict = None):
        """Initializes the Config object with the given configuration. If no configuration is provided, an empty dictionary is used.

        Args:
            config (dict): The configuration to set. If None, an empty dictionary is used.
        """
        if config is None:
            self.config = {}
        else:
            self.config = config

    # Return the Config
    def getConfig(self) -> dict:
        """Returns the current configuration/settings in a dict (parsed JSON data).

        Returns:
            dict: Parsed JSON data.
        """
        return self.config

    # Sets the Config
    def setConfig(self, config: dict):
        """Sets the current configuration/settings. This method is used to update the configuration settings in the object.

        Args:
            config (dict): The Config to set.
        """
        self.config = config
        
    # Loads Config from JSON Config File
    def LoadConfig(self):
        """
        Loads the JSON configuration file.
        """
        try:
            with open(CONFIG_PATH, 'r') as file:
                self.config = json.load(file)
                return
            
        # If no Config file present -> Create a new Config an load it    
        except FileNotFoundError:
            print(f"Configuration file not found. Creating a new one at {CONFIG_PATH}.")
            CreateEmptyConfig()
            self.LoadConfig()
            return
        
        # If there is a problem reading the Config file
        except json.JSONDecodeError as e:
            print(f"Error reading JSON file: {e}")
            return
        
    # Update the Config file and return updated config
    def UpdateConfig(self, key_path: list, value):
        """
        Updates the JSON configuration file with a new value at the specified key path.

        Args:
            key_path (list): A list representing the nested keys to the target value.
            value (Any): The value to set at the specified key path.
        """
        try:
            if self.config != {}:
                # Traverse to the correct location in the nested structure
                current = self.config
                for key in key_path[:-1]:
                    if key not in current or not isinstance(current[key], dict):
                        current[key] = {}
                    current = current[key]

                # Set the value at the final key
                current[key_path[-1]] = value

                # Save back to file
                with open(CONFIG_PATH, 'w') as file:
                    json.dump(self.config, file, indent=4)   
                    
            else:
                print("Error: Config is empty. Cannot update empty Config.")

            return
        
        except Exception as e:
            print(f"Error updating configuration file: {e}")
            return
        
    def getCustomCommands(self):
        pass
    
    # Getters for Config data
    def getTimezone(self):
        try:
            timezone = self.config["userSettings"]["timezone"]
            return timezone
        
        except Exception as e:
            print(f"Error getting timezone: {e}")
            return None  
    
    
    def getAltTimezone(self):
        try: 
            altTimezone = self.config["userSettings"]["altTimezone"]
            return altTimezone
        
        except Exception as e:
            print(f"Error getting altTimezone: {e}")
            return None 
    
    
    def getPrefix(self):
        try: 
            prefix = self.config["userSettings"]["prefix"]
            return prefix
        
        except Exception as e:
            print(f"Error getting Prefix: {e}")
            return None


# GOTO - Basic Create/Load/Update Config

# Create empty Config file if not present 
def CreateEmptyConfig():
    """
    Creates an empty JSON configuration file with a "commands" key.

    Args:
        file_path (str): Path to the JSON file.
    """
    try:
        with open(CONFIG_TEMPLATE_PATH, 'r') as template_file:
            template_config = json.load(template_file)

        with open(CONFIG_PATH, 'w') as new_file:
            json.dump(template_config, new_file, indent=4)
        print(f"Configuration file created from template at {CONFIG_PATH}")

    except FileNotFoundError:
        print(f"Template file '{CONFIG_TEMPLATE_PATH}' not found. Unable to create configuration file.")

    except json.JSONDecodeError as e:
        print(f"Error reading template file: {e}")
        
    except Exception as e:
        print(f"Error creating configuration file: {e}")

# TODO: Needs a rewrite
# Update the Config file and return updated config
def updateCommandConfig(command_name):
    """
    Updates the JSON configuration file with a new entry in the "commands" array.

    Args:
        file_path (str): Path to the JSON file.
        command_name (str): Name of the new command.

    Returns:
        dict: The updated configuration.
    """
    try:
        # Load existing config
        cfg = Config(Config.LoadConfig())

        # Ensure "commands" is a list
        if "commands" not in cfg.config or not isinstance(cfg.config["commands"], list):
            cfg.config["commands"] = []

        # Add the command if it doesn't already exist
        if command_name not in cfg.config["commands"]:
            cfg.config["commands"].append(command_name)

        # Save back to file and return updated config
        with open(CONFIG_PATH, 'w') as file:
            json.dump(cfg.config, file, indent=4)
        print(f"Command '{command_name}' added to the configuration file.")
        return cfg.config    
    
    except Exception as e:
        print(f"Error updating configuration file: {e}")
        return None



# GOTO - Read Config Objects

# TODO: Needs a rewrite
# Reads the Command Section of the Config
def readCommandConfig(data):
    """
    Creates an Enum from the "commands" object in a JSON file.

    Args:
        data (any): the data object containing the loaded JSON Config.

    Returns:
        Enum: An Enum class with entries derived from the "commands" object.
    """
    try:
        
        # Check if "commands" key exists
        if "commands" not in data:
            raise KeyError("The JSON file does not contain a 'commands' key.")

        # Extract command names
        commands = data["commands"]
        if not isinstance(commands, list):
            raise ValueError("The 'commands' key must contain an object (dictionary).")

        # Dynamically create the Enum
        CommandEnum = Enum("CommandEnum", {name: name for name in commands})

        return CommandEnum

    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error reading JSON file: {e}")
        return None
    except (KeyError, ValueError) as e:
        print(f"Error processing JSON content: {e}")
        return None

# TODO: Needs a rewrite
# Reads the Command Section of the Config
def readCounterConfig(data):
    """
    Creates an Enum from the "commands" object in a JSON file.

    Args:
        data (any): the data object containing the loaded JSON Config.

    Returns:
        Enum: An Enum class with entries derived from the "commands" object.
    """
    try:
        
        # Check if "commands" key exists
        if "counters" not in data:
            raise KeyError("The JSON file does not contain a 'counters' key.")

        # Extract command names
        counters = data["counters"]
        # if not isinstance(counters, dict):
            # raise ValueError("The 'commands' key must contain an object (dictionary).")

        # Dynamically create the Enum and Array
        counter_array = [[name, obj.get('counter', 0)] for name, obj in counters.items()]
        CounterEnum = Enum('CounterEnum', {name.upper(): idx for idx, (name, _) in enumerate(counter_array)})

        return CounterEnum, counter_array

    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error reading JSON file: {e}")
        return None
    except (KeyError, ValueError) as e:
        print(f"Error processing JSON content: {e}")
        return None 
    
# TODO: Needs a rewrite
# Reads the List Section of the Config
def readQueueConfig(data):
    """
    Creates an Enum from the "queue" object in a JSON file.

    Args:
        data (any): the data object containing the loaded JSON Config.

    Returns:
        Enum: An Enum class with entries derived from the "queue" object.
    """
    try:
        
        # Check if "queue" key exists
        if "lists" not in data:
            raise KeyError("The JSON file does not contain a 'queue' key.")

        # Extract command names
        player_list = data["lists"]["queue"]["players"]
        joinable = data["lists"]["queue"]["joinable"]
        multiJoin = data["lists"]["queue"]["multiJoin"]
        # if not isinstance(queue, dict):
            # raise ValueError("The 'queue' key must contain an object (dictionary).")

        # Return Queue Object
        return Queue(player_list, multiJoin, joinable)

    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error reading JSON file: {e}")
        return None
    except (KeyError, ValueError) as e:
        print(f"Error processing JSON content: {e}")
        return None 
