# .env
import os
from dotenv import find_dotenv, load_dotenv

from spotipy import Spotify
from spotipy.oauth2 import SpotifyOAuth



envPath = find_dotenv()
load_dotenv(envPath)

SPOTIPY_CLIENT_ID = os.getenv("SPOTIFY_ID")
SPOTIPY_CLIENT_SECRET = os.getenv("SPOTIFY_SECRET")
SPOTIPY_REDIRECT_URI = os.getenv("SPOTIPY_REDIRECT_URI")
# SPO_TOKEN = os.getenv("SPOTIFY_REFRESH_TOKEN")

scope = "user-library-read, user-modify-playback-state, user-read-playback-state"

spOAuth = SpotifyOAuth(
    client_id=SPOTIPY_CLIENT_ID,
    client_secret=SPOTIPY_CLIENT_SECRET,
    redirect_uri=SPOTIPY_REDIRECT_URI,
    scope=scope,
    show_dialog=True
)

sp = Spotify(auth_manager=spOAuth)


# GOTO - Spotify API Functions

# Function | Add Track to Queue
async def addTrackToQueue (uri):
    """Adds a Track to the Queue.

    Args:
        uri (string): URL to the Track.

    Returns:
        string or None: None if successful. Error Messages when function fails.
    """
    try:
        sp.add_to_queue(uri=uri)
        return None
    except Exception as e:
        return e.message