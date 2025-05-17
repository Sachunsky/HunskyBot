# .env
import os
from dotenv import find_dotenv, load_dotenv

# Twitch API Imports
from twitchAPI.chat import Chat, EventData, ChatMessage, ChatSub, ChatCommand
from twitchAPI.type import AuthScope, ChatEvent, ChatRoom
from twitchAPI.oauth import UserAuthenticator
from twitchAPI.twitch import Twitch

import customCommands as CustomCommands
from config import Config
import config

# Misc
import asyncio
import random
from enum import Enum


# Loading .env file
envPath = find_dotenv()
load_dotenv(envPath)

# Load Environment Variables
OAUTH_TOKEN = os.getenv("OAUTH_TOKEN")
SECRET = os.getenv("SECRET")
APP_ID = os.getenv("CLIENT_ID")
USER_SCOPE = [AuthScope.CHAT_READ, AuthScope.CHAT_EDIT, AuthScope.CHANNEL_MANAGE_BROADCAST]
TARGET_CHANNEL = os.getenv("CHANNEL")
TOKEN = os.getenv('TOKEN')
REFRESH_TOKEN = os.getenv('REFRESH_TOKEN')
CONFIG_PATH = os.getenv('CONFIG_PATH')



# GOTO - Common Event Listeners

# Event Listener | Read chat messages
async def onMessage(msg: ChatMessage):
# Print Username and message
    print(f'{msg.user.display_name} - {msg.text}')

# Event Listener | Bot connected
async def onConnect(connectEvent: EventData):
# Connect to target channel
    await connectEvent.chat.join_room(TARGET_CHANNEL)

    print('Bot connected')



# GOTO - BOT Init

# Function | Bot initializer
async def runBot():
    # Authenticate app
    bot = await Twitch(APP_ID, SECRET)
    auth = UserAuthenticator(bot, USER_SCOPE)
    # token, refresh_token = await auth.authenticate()
    # print(token)
    # print(refresh_token)
    await bot.set_user_authentication(TOKEN, USER_SCOPE, REFRESH_TOKEN)
    
    # Initialize chat class
    chat = await Chat(bot)

    # Load Config from config.json
    cfg = Config()
    cfg.LoadConfig()
    cmdList: Enum = ConfigManager.readCommandConfig(cfg.config)

    # Register Common Events
    chat.register_event(ChatEvent.READY, onConnect)
    chat.register_event(ChatEvent.MESSAGE, onMessage)


# TODO: Rewrite to use new Middleware and new command system
    # Register commands
    for cmd in cmdList:
        chat.register_command(cmd.name, getattr(CustomCommands, f'{cmd.name}_command'))

    # Start the chat bot
    chat.start()

    try:
        input('press Enter to stop  \n')
    finally:
        chat.stop()
        await bot.close()


# Bot Start
asyncio.run(runBot())
