from googleapiclient.discovery import build
from urllib.parse import urlparse, parse_qs
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from tqdm import tqdm
from difflib import SequenceMatcher
import os
from dotenv import load_dotenv
import re

# =========================
# youtube helpers
# =========================

def get_playlist_id(url):
    query = parse_qs(urlparse(url).query)
    return query.get("list", [None])[0]

def get_playlist_songs(youtube, playlist_id):
    all_items = []
    next_page_token = None

    while True:
        request = youtube.playlistItems().list(
            part="snippet",
            playlistId=playlist_id,
            maxResults=50,
            pageToken=next_page_token
        )

        response = request.execute()
        all_items.extend(response["items"])

        next_page_token = response.get("nextPageToken")
        if not next_page_token:
            break

    return all_items

def get_playlist_title(youtube, playlist_id):
    yt_playlist = youtube.playlists().list(
        part="snippet",
        id=playlist_id
    ).execute()

    return yt_playlist["items"][0]["snippet"]["title"]

# =========================
# text utilities
# =========================

def clean(text):
    text = re.sub(r"\(.*?\)", "", text)
    text = re.sub(r"\[.*?\]", "", text)
    return text.strip()

def normalize(text):
    text = text.lower()
    text = re.sub(r"[^a-z0-9 ]", "", text)
    return re.sub(r"\s+", " ", text).strip()

def safe_query(text, max_len=120):
    return text.strip()[:max_len]

# =========================
# parsing
# =========================

def parse_video_title(title):
    title = clean(title)

    for sep in [" - ", " – ", ":"]:
        if sep in title:
            artist, track = title.split(sep, 1)
            return artist.strip(), track.strip()

    return None, title.strip()

def parse_description(desc):
    matches = re.findall(r"(.+?)\s*[·\-–]\s*(.+)", desc)
    return [(right.strip(), left.strip()) for left, right in matches]

# =========================
# scoring
# =========================

def score(track, artist, sp_track):
    sp_name = normalize(sp_track["name"])
    sp_artist = normalize(sp_track["artists"][0]["name"])

    track_score = SequenceMatcher(None, normalize(track), sp_name).ratio()

    artist_score = 0
    if artist:
        artist_score = SequenceMatcher(None, normalize(artist), sp_artist).ratio()

    return (0.6 * track_score) + (1.4 * artist_score)

def artist_match_ok(artist, sp_artist, threshold=0.75):
    if not artist:
        return True
    return SequenceMatcher(
        None,
        normalize(artist),
        normalize(sp_artist)
    ).ratio() >= threshold

# =========================
# chunking
# =========================

def chunk_list(lst, size):
    for i in range(0, len(lst), size):
        yield lst[i:i + size]


def main():
    load_dotenv()

    youtube = build("youtube", "v3", developerKey=os.getenv("YOUTUBE_KEY"))

    playlist_url = input("YouTube playlist URL: ")
    genre = input("Genre (edm, techno, etc): ").strip().lower()

    playlist_id = get_playlist_id(playlist_url)
    songs = get_playlist_songs(youtube, playlist_id)

    sp = spotipy.Spotify(
        auth_manager=SpotifyOAuth(
            client_id=os.getenv("SPOTIFY_CLIENT_ID"),
            client_secret=os.getenv("SPOTIFY_CLIENT_SECRET"),
            redirect_uri=os.getenv("SPOTIFY_REDIRECT_URI"),
            scope="playlist-modify-private"
        )
    )

    track_uris = []
    seen = set()

    for item in tqdm(songs, desc="Searching Spotify"):
        s = item["snippet"]

        title = s["title"]
        desc = s.get("description", "")
        channel = s.get("channelTitle", "")

        candidates = []

        # 1. description (best signal)
        candidates.extend(parse_description(desc))

        # 2. fallback title
        artist, track = parse_video_title(title)
        if track:
            candidates.append((artist, track))

        for artist, track in candidates:
            if not track:
                continue

            key = normalize(f"{artist or ''} {track}")
            if key in seen:
                continue
            seen.add(key)

            if artist:
                query = f"{artist} {track} {genre}"
            else:
                query = f"{track} {channel} {genre}"

            query = safe_query(query)

            results = sp.search(q=query, type="track", limit=5)
            items = results["tracks"]["items"]

            if not items:
                continue

            best = None
            best_score = 0

            for it in items:
                sp_artist = it["artists"][0]["name"]
                
                if not artist_match_ok(artist, sp_artist):
                    continue

                s = score(track, artist, it)

                if s > best_score:
                    best_score = s
                    best = it

            if best and best_score > 0.55:
                uri = best["uri"]
                if uri not in track_uris:
                    track_uris.append(uri)

    print("\nTOTAL FOUND:", len(track_uris))

    playlist = sp.user_playlist_create(
        user=sp.current_user()["id"],
        name=get_playlist_title(youtube, playlist_id),
        public=False
    )

    for chunk in chunk_list(track_uris, 100):
        sp.playlist_add_items(playlist["id"], chunk)

if __name__ == "__main__":
    main()