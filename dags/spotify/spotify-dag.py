import json
import os
from collections import defaultdict

import pandas as pd
import spotipy
from dotenv import load_dotenv
from spotipy.oauth2 import SpotifyOAuth

load_dotenv()
CLIENT_ID: str = os.environ["CLIENT_ID"]
CLIENT_SECRET: str = os.environ["CLIENT_SECRET"]

redirect_uri: str = "https://google.com/"

auth_manager = SpotifyOAuth(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    redirect_uri=redirect_uri,
    scope=["user-read-recently-played"],
)
spotify = spotipy.Spotify(auth_manager=auth_manager)

recent_plays = spotify.current_user_recently_played(limit=50)
with open("recent_plays.json", mode="w") as f:
    json.dump(recent_plays, f)

history = defaultdict(list)

for n, item in enumerate(recent_plays["items"]):
    history["artist_id"].append(item["track"]["artists"][0]["id"])
    history["artists_name"].append(item["track"]["artists"][0]["name"])
    history["track_id"].append(item["track"]["id"])
    history["track_name"].append(item["track"]["name"])
    history["time_played"].append(item["played_at"])
    history["duration_ms"].append(item["track"]["duration_ms"])
    history["is_explicit"].append(item["track"]["explicit"])
    history["is_album"].append(
        True if (item["track"]["album"]["album_type"] == "album") else False
    )
    # next_url = recent_plays["next"]
    # history["track_release_date"] = item["track"]["release_date"]

history_df = pd.DataFrame(history)
history_df
