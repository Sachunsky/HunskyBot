import asyncio
import os

from dotenv import load_dotenv
from twitchAPI.oauth import UserAuthenticator
from twitchAPI.twitch import Twitch
from twitchAPI.type import AuthScope

load_dotenv()

app_id = os.getenv("CLIENT_ID", "")
secret = os.getenv("SECRET", "")
token = os.getenv("TOKEN", "")
refresh_token = os.getenv("REFRESH_TOKEN", "")
channel = os.getenv("CHANNEL", "")
config_path = os.getenv("CONFIG_PATH", "config/config.json")


async def get_token():
    twitch = await Twitch(app_id, secret)
    scopes = [
        AuthScope.CHAT_READ,
        AuthScope.CHAT_EDIT,
        AuthScope.CHANNEL_MANAGE_BROADCAST,
    ]
    auth = UserAuthenticator(twitch, scopes)
    token, refresh_token = await auth.authenticate()
    print(f"TOKEN={token}")
    print(f"REFRESH_TOKEN={refresh_token}")


asyncio.run(get_token())
