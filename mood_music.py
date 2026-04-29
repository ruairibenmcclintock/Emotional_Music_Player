# mood_music.py
import requests
import json

API_KEY = #input Last.Fm API here at https://www.last.fm/api 
BASE_URL = 'http://ws.audioscrobbler.com/2.0/'

def generate_song_list(input_file="assistant_output.json", output_file="song_list.json"):
    with open(input_file, 'r') as file:
        data = json.load(file)

    tag_weights = data["recommended_tags"]
    suggested_genres = set(genre.lower() for genre in data.get("suggested_genres", []))

    def get_songs_by_tag(tag, limit=5):
        params = {'method': 'tag.gettoptracks', 'tag': tag, 'api_key': API_KEY, 'format': 'json', 'limit': limit}
        response = requests.get(BASE_URL, params=params)
        if response.status_code == 200:
            try:
                return [(t['name'], t['artist']['name']) for t in response.json()['tracks']['track']]
            except KeyError:
                return []
        return []

    def get_track_tags(artist, track):
        params = {'method': 'track.gettoptags', 'artist': artist, 'track': track, 'api_key': API_KEY, 'format': 'json'}
        response = requests.get(BASE_URL, params=params)
        if response.status_code == 200:
            try:
                return [tag['name'].lower() for tag in response.json()['toptags']['tag']]
            except (KeyError, TypeError):
                return []
        return []

    def matched_genres(tags):
        return [g for g in suggested_genres if g in tags]

    song_info = {}

    for entry in tag_weights:
        tag = entry["tag"]
        weight = entry.get("weight", 1.0)
        for title, artist in get_songs_by_tag(tag):
            key = (title, artist)
            song_info.setdefault(key, {"score": 0, "source_tags": set(), "track_tags": [], "matched_genres": []})
            song_info[key]["score"] += weight
            song_info[key]["source_tags"].add(tag)

    for key in song_info:
        title, artist = key
        tags = get_track_tags(artist, title)
        song_info[key]["track_tags"] = tags
        song_info[key]["matched_genres"] = matched_genres(tags)
        if song_info[key]["matched_genres"]:
            song_info[key]["score"] += 0.5

    # Sort songs by score
    sorted_songs = sorted(song_info.items(), key=lambda x: x[1]["score"], reverse=True)

    # Limit the result to 10 songs only
    sorted_songs = sorted_songs[:10]

    output = {"song_list": [{"title": title, "artist": artist} for (title, artist), _ in sorted_songs]}
    with open(output_file, "w") as f:
        json.dump(output, f, indent=2)

    return sorted_songs
