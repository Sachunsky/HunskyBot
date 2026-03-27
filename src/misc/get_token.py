import asyncio

from twitchAPI.oauth import UserAuthenticator
from twitchAPI.twitch import Twitch
from twitchAPI.type import AuthScope


async def get_token():
    twitch = await Twitch(
        "9uw3vi3q2gtv80x42lme8avuam8j7r", "lvoc0tclx418wynmbjattw637psgrb"
    )
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
