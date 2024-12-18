# Twitch API Imports
from twitchAPI.chat import Chat, EventData, ChatMessage, ChatSub, ChatCommand
from twitchAPI.type import AuthScope, ChatEvent, ChatRoom
from twitchAPI.oauth import UserAuthenticator
from twitchAPI.twitch import Twitch

# Misc
import os, json, asyncio, random
from dotenv import find_dotenv, load_dotenv
from enum import Enum


# Loading .env file
envPath = find_dotenv()
load_dotenv(envPath)

# Load Environment Variables
CONFIG_TEMPLATE_PATH = os.getenv('CONFIG_TEMPLATE_PATH')


# GOTO - Basic Create/Load/Update Config

# Loads Config from JSON Config File
def loadConfig(file_path):
    """
    Loads the JSON configuration file and returns its content as a dictionary.

    Args:
        file_path (str): Path to the JSON file.

    Returns:
        dict: Parsed JSON data.
    """
    try:
        with open(file_path, 'r') as file:
            return json.load(file)
        
    # If no Config file present -> Create a new Config an load it    
    except FileNotFoundError:
        print(f"Configuration file not found. Creating a new one at {file_path}.")
        createEmptyConfig(file_path)
        return loadConfig(file_path)
    
    # If there is a problem reading the Config file
    except json.JSONDecodeError as e:
        print(f"Error reading JSON file: {e}")
        return None

# Create empty Config file if not present 
def createEmptyConfig(file_path):
    """
    Creates an empty JSON configuration file with a "commands" key.

    Args:
        file_path (str): Path to the JSON file.
    """
    try:
        with open(CONFIG_TEMPLATE_PATH, 'r') as template_file:
            template_config = json.load(template_file)

        with open(file_path, 'w') as new_file:
            json.dump(template_config, new_file, indent=4)
        print(f"Configuration file created from template at {file_path}")

    except FileNotFoundError:
        print(f"Template file '{CONFIG_TEMPLATE_PATH}' not found. Unable to create configuration file.")

    except json.JSONDecodeError as e:
        print(f"Error reading template file: {e}")
        
    except Exception as e:
        print(f"Error creating configuration file: {e}")

# Update the Config file and return updated config
def updateConfig(file_path, key_path, value):
    """
    Updates the JSON configuration file with a new value at the specified key path.

    Args:
        file_path (str): Path to the JSON file.
        key_path (list): A list representing the nested keys to the target value.
        value (Any): The value to set at the specified key path.

    Returns:
        dict: The updated configuration.
    """
    try:
        # Load existing config
        config = loadConfig(file_path)

        # Traverse to the correct location in the nested structure
        current = config
        for key in key_path[:-1]:
            if key not in current or not isinstance(current[key], dict):
                current[key] = {}
            current = current[key]

        # Set the value at the final key
        current[key_path[-1]] = value

        # Save back to file
        with open(file_path, 'w') as file:
            json.dump(config, file, indent=4)
        # print(f"Configuration updated: {' -> '.join(key_path)} = {value}")

        return config
    except Exception as e:
        print(f"Error updating configuration file: {e}")
        return None

# Update the Config file and return updated config
def updateCommandConfig(file_path, command_name):
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
        config = loadConfig(file_path)

        # Ensure "commands" is a list
        if "commands" not in config or not isinstance(config["commands"], list):
            config["commands"] = []

        # Add the command if it doesn't already exist
        if command_name not in config["commands"]:
            config["commands"].append(command_name)

        # Save back to file and return updated config
        with open(file_path, 'w') as file:
            json.dump(config, file, indent=4)
        print(f"Command '{command_name}' added to the configuration file.")
        return config
    
    
    except Exception as e:
        print(f"Error updating configuration file: {e}")
        return None


# GOTO - Read Config Objects

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
    
