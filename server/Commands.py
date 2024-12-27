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
from ConfigManager import Queue


# Loading .env file
envPath = find_dotenv()
load_dotenv(envPath)

# Load Environment Variables
TARGET_CHANNEL = os.getenv("CHANNEL")
CONFIG_PATH = os.getenv("CONFIG_PATH")

# Load Config
config = ConfigManager.loadConfig(CONFIG_PATH)
counters, counter_array = ConfigManager.readCounterConfig(config)
commandList = ConfigManager.readCommandConfig(config)
queue  = ConfigManager.readQueueConfig(config)



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
    ConfigManager.updateConfig(CONFIG_PATH, ['counters', counter_array[counters.LOST.value][0], 'counter'], counter_array[counters.LOST.value][1])

    await cmd.chat.send_message(f'#{TARGET_CHANNEL}', f'@Sachunsky ist zum {counter_array[counters.LOST.value][1]}-mal so orientierungslos wie ein Navi ohne GPS! WaitWhat catJAM')

# Event Listener | Timer Command | DEAD 
async def dead_command(cmd: ChatMessage):
    counter_array[counters.DEAD.value][1] += 1 
    ConfigManager.updateConfig(CONFIG_PATH, ['counters', counter_array[counters.DEAD.value][0], 'counter'], counter_array[counters.DEAD.value][1])

    await cmd.chat.send_message(f'#{TARGET_CHANNEL}', f'@Sachunsky geht nun schon zum {counter_array[counters.DEAD.value][1]}-mal im Himmel die Patchnotes lesen! Sadge RIP')

# Event Listener | Timer Command | MIST 
async def mist_command(cmd: ChatMessage):
    counter_array[counters.MIST.value][1] += 1 
    ConfigManager.updateConfig(CONFIG_PATH, ['counters', counter_array[counters.MIST.value][0], 'counter'], counter_array[counters.MIST.value][1])

    await cmd.chat.send_message(f'#{TARGET_CHANNEL}', f'@Sachunsky macht zum {counter_array[counters.MIST.value][1]}-mal nur Mist! NOPERS ThisIsFine')



# GOTO - Queue & Giveaway Lists

# Event Listener | Command | QUEUE
async def queue_command(cmd: ChatMessage):

    # !queue - shows the queue
    if cmd.text == '!queue':
        queueMessage = ''

        for index in range(len(queue.players)):
            queueMessage = queueMessage + f' - #{index + 1}: @{queue.players[index]}'

        await cmd.chat.send_message(f'#{TARGET_CHANNEL}', f'Queue Liste{queueMessage}')
        return
    

    # !queue open - opens the queue
    if cmd.text == '!queue open':
        if cmd.user.mod or cmd.user.name == TARGET_CHANNEL:
            queue.setJoinable(True)
            ConfigManager.updateConfig(CONFIG_PATH, ['lists', 'queue', 'joinable'], True)
            
            await cmd.chat.send_message(f'#{TARGET_CHANNEL}', f'Die Queue ist nun geöffnet! Schreib "!queue join" um dich in die Warteschlange einzutragen. "!queue leave" um dich abzumelden.')
            return

        else:
            await cmd.chat.send_message(f'#{TARGET_CHANNEL}', f'Nix da @{cmd.user.name}. Du bist kein Moderator!')
            return


    # !queue close - closes the queue
    if cmd.text == '!queue close':
        if cmd.user.mod or cmd.user.name == TARGET_CHANNEL:
            queue.setJoinable(False)
            ConfigManager.updateConfig(CONFIG_PATH, ['lists', 'queue', 'joinable'], True)

            await cmd.chat.send_message(f'#{TARGET_CHANNEL}', f'Die Queue ist nun geschlossen!')
            return
        
        else:
            await cmd.chat.send_message(f'#{TARGET_CHANNEL}', f'Nix da @{cmd.user.name}. Du bist kein Moderator!')
            return


    # !queue multi - toggles the multiJoin status of the queue
    if cmd.text == '!queue multi':
        if cmd.user.mod or cmd.user.name == TARGET_CHANNEL:
            queue.setMultiJoin(not queue.multiJoin)
            ConfigManager.updateConfig(CONFIG_PATH, ['lists', 'queue', 'multiJoin'], queue.multiJoin)

            if queue.multiJoin:
                await cmd.chat.send_message(f'#{TARGET_CHANNEL}', f'Multi-Join ist nun aktiviert! Jeder kann sich mehrfach in die Queue eintragen.')
                return

            else:
                await cmd.chat.send_message(f'#{TARGET_CHANNEL}', f'Multi-Join ist nun deaktiviert! Jeder kann sich nur einmal in die Queue eintragen.')
                return
        
        else:
            await cmd.chat.send_message(f'#{TARGET_CHANNEL}', f'Nix da @{cmd.user.name}. Du bist kein Moderator!')
            return
        

    # !queue save - saves the queue to the config
    if cmd.text == '!queue save':
        if cmd.user.mod or cmd.user.name == TARGET_CHANNEL:
            ConfigManager.updateConfig(CONFIG_PATH, ['lists', 'queue', 'players'], queue.players)

            await cmd.chat.send_message(f'#{TARGET_CHANNEL}', f'Die Queue wurde gespeichert!')
            return
        
        else:
            await cmd.chat.send_message(f'#{TARGET_CHANNEL}', f'Nix da @{cmd.user.name}. Du bist kein Moderator!')
            return    

    # !queue reset - resets the queue
    if cmd.text == '!queue reset':
        if cmd.user.mod or cmd.user.name == TARGET_CHANNEL:
            queue.players = []
            ConfigManager.updateConfig(CONFIG_PATH, ['lists', 'queue', 'players'], [])

            await cmd.chat.send_message(f'#{TARGET_CHANNEL}', f'Die Queue wurde geleert!')
            return
        
        else:
            await cmd.chat.send_message(f'#{TARGET_CHANNEL}', f'Nix da @{cmd.user.name}. Du bist kein Moderator!')
            return
        
    
    # !queue next - removes the first player from the queue
    if cmd.text == '!queue next':
        if cmd.user.mod or cmd.user.name == TARGET_CHANNEL:
            if len(queue.players) > 0:
                nextPlayer = queue.players.pop(0)

                await cmd.chat.send_message(f'#{TARGET_CHANNEL}', f'@{nextPlayer} ist an der Reihe!')
                return
            
            else:
                await cmd.chat.send_message(f'#{TARGET_CHANNEL}', f'Die Queue ist leer! D:')
                return
        
        else: 
            await cmd.chat.send_message(f'#{TARGET_CHANNEL}', f'Nix da @{cmd.user.name}. Du bist kein Moderator!')
            return


    # !queue remove - removes all instanced of a user from the queue
    if cmd.text.startswith('!queue remove '):
        if cmd.user.mod or cmd.user.name == TARGET_CHANNEL:
            removedUser = cmd.text.replace('!queue remove ', '')
            if removedUser.startswith('@'):
                removedUser = removedUser.replace('@', '')

            queue.removePlayerAllInstances(removedUser)

            await cmd.chat.send_message(f'#{TARGET_CHANNEL}', f'@{removedUser} wurde aus der Queue entfernt!')
            return
        
        else: 
            await cmd.chat.send_message(f'#{TARGET_CHANNEL}', f'Nix da @{cmd.user.name}. Du bist kein Moderator!')
            return


    # !queue join - adds a user to the queue
    if cmd.text == '!queue join':
        if queue.joinable:
            if not queue.multiJoin:
                if queue.players.count(cmd.user.name) == 0:
                    queue.addPlayer(cmd.user.name)
                    await cmd.chat.send_message(f'#{TARGET_CHANNEL}', f'@{cmd.user.name} ist der Queue beigetreten!')
                    return
            
                else:
                    await cmd.chat.send_message(f'#{TARGET_CHANNEL}', f'@{cmd.user.name} ist bereits in der Queue!')
                    return

            queue.addPlayer(cmd.user.name)

            await cmd.chat.send_message(f'#{TARGET_CHANNEL}', f'@{cmd.user.name} ist der Queue beigetreten!')
            return
        
        else:
            await cmd.chat.send_message(f'#{TARGET_CHANNEL}', f'Die Queue ist momentan geschlossen!')
            return


    # !queue leave - removes the first instance of a user from the queue
    if cmd.text == '!queue leave':
        queue.removePlayer(cmd.user.name)

        await cmd.chat.send_message(f'#{TARGET_CHANNEL}', f'@{cmd.user.name} hat die Queue verlassen!')
        return


