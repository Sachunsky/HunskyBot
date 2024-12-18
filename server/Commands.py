# Twitch API Imports
from twitchAPI.chat import Chat, EventData, ChatMessage, ChatSub, ChatCommand
from twitchAPI.type import AuthScope, ChatEvent, ChatRoom
from twitchAPI.oauth import UserAuthenticator
from twitchAPI.twitch import Twitch

# Misc imports
import os, json, asyncio, random
from dotenv import find_dotenv, load_dotenv
from enum import Enum

# Project specific imports
import ConfigManager


# Loading .env file
envPath = find_dotenv()
load_dotenv(envPath)

# Load Environment Variables
TARGET_CHANNEL = os.getenv("CHANNEL")
CONFIG_PATH = os.getenv("CONFIG_PATH")
CHANNEL = os.getenv("CHANNEL")

# Load Config
config = ConfigManager.loadConfig(CONFIG_PATH)
counters, counter_array = ConfigManager.readCounterConfig(config)
commandList = ConfigManager.readCommandConfig(config)


# GOTO - COMMON COMMANDS

# Event Listener | Command | HELP
async def help_command(cmd: ChatMessage):
    cmdList = ''
    for command in commandList:
        cmdList = cmdList + '!' + command.value + ', '
    await cmd.chat.send_message(f'#{TARGET_CHANNEL}', f'Enabled Commands: {cmdList}')  

# Event Listener | Command | LURK
async def lurk_command(cmd: ChatMessage):
    dice = random.randint(0, 3)

    if dice == 0:
        await cmd.chat.send_message(f'#{TARGET_CHANNEL}', f'@{cmd.user.name}  verschwindet in\'s Gebüsch Lurking ... Möge der Lurk mit dir sein! catLurk')    
    elif dice == 1:
        await cmd.chat.send_message(f'#{TARGET_CHANNEL}', f'@{cmd.user.name} hat den Tarnmodus aktiviert. Lurking Danke fürs Lurken und die Unterstützung! PETTHECHAT')  
    elif dice == 2:
        await cmd.chat.send_message(f'#{TARGET_CHANNEL}', f'@{cmd.user.name}  ist AFK gegangen, aber XP fürs Lurken gibt\'s trotzdem! GoodGame Danke für den Support!')  
    elif dice == 3:
        await cmd.chat.send_message(f'#{TARGET_CHANNEL}', f'@{cmd.user.name}  hat den Chat in den Hintergrundprozess verschoben. robotD CPU-Auslastung: 0%, Support-Level: 100%!')  


# GOTO - COUNTERS

# Event Listener | Timer Command | LOST 
async def lost_command(cmd: ChatMessage):
    counter_array[counters.LOST.value][1] += 1 
    ConfigManager.updateCounterConfig(CONFIG_PATH, ['counters', counter_array[counters.LOST.value][0], 'counter'], counter_array[counters.LOST.value][1])

    await cmd.chat.send_message(f'#{TARGET_CHANNEL}', f'@Sachunsky ist zum {counter_array[counters.LOST.value][1]}-mal so orientierungslos wie ein Navi ohne GPS! WaitWhat catJAM')

# Event Listener | Timer Command | DEAD 
async def dead_command(cmd: ChatMessage):
    counter_array[counters.DEAD.value][1] += 1 
    ConfigManager.updateCounterConfig(CONFIG_PATH, ['counters', counter_array[counters.DEAD.value][0], 'counter'], counter_array[counters.DEAD.value][1])

    await cmd.chat.send_message(f'#{TARGET_CHANNEL}', f'@Sachunsky geht nun schon zum {counter_array[counters.DEAD.value][1]}-mal im Himmel die Patchnotes lesen! Sadge RIP')

# Event Listener | Timer Command | MIST 
async def mist_command(cmd: ChatMessage):
    counter_array[counters.MIST.value][1] += 1 
    ConfigManager.updateCounterConfig(CONFIG_PATH, ['counters', counter_array[counters.MIST.value][0], 'counter'], counter_array[counters.MIST.value][1])

    await cmd.chat.send_message(f'#{TARGET_CHANNEL}', f'@Sachunsky macht zum {counter_array[counters.MIST.value][1]}-mal nur Mist! NOPERS ThisIsFine')