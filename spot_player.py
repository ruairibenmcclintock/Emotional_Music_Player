# spot_player.py
import json
import time
from spotipy.oauth2 import SpotifyOAuth
import spotipy
import tkinter as tk

CLIENT_ID = '' #input Spotify API key here
CLIENT_SECRET = '' #input Secret client key here
#above can be accessed here https://developer.spotify.com/documentation/web-api

REDIRECT_URI = 'http://127.0.0.1:8000/callback'
scope = 'user-modify-playback-state user-read-playback-state'

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=CLIENT_ID, client_secret=CLIENT_SECRET, redirect_uri=REDIRECT_URI, scope=scope))

def play_song_list(output_box, file="song_list.json"):  # Added output_box as a parameter
    with open(file, 'r') as f:
        songs = json.load(f)['song_list']

    for song in songs:
        query = f"track:{song['title']} artist:{song['artist']}"
        results = sp.search(q=query, limit=1, type='track')
        if results['tracks']['items']:
            track_uri = results['tracks']['items'][0]['uri']
            sp.add_to_queue(track_uri)
            output_box.insert(tk.END, f"Added to queue: {song['title']} by {song['artist']}\n")
            output_box.yview(tk.END)
            time.sleep(1)
        else:
            output_box.insert(tk.END, f"Song not found: {song['title']} by {song['artist']}\n")
            output_box.yview(tk.END)
