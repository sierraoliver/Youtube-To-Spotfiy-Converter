# Youtube-To-Spotfiy-Converter
<h2>Description</h2>

This project was created to reduce the hassle of moving playlists from YouTube to Spotify.

Instead of manually searching for every song, this application takes a YouTube playlist URL, attempts to find the best matching songs on Spotify using metadata and similarity matching, and automatically creates a Spotify playlist.

The project is currently being expanded with a Flask-based UI to allow better playlist visualization and side-by-side comparison between YouTube and Spotify matches.


------------------------------------------------------------------------------------
## Features

- Extract songs from YouTube playlists
- Parse song titles, artists, channel names, and descriptions
- Search Spotify for the best matching tracks
- Similarity scoring system to improve match accuracy
- Automatic Spotify playlist creation
- Duplicate prevention system
- Progress bar while searching tracks
- Support for large playlists (200+ songs)

------------------------------------------------------------------------------------
## Installation

Clone the repository:

```bash
git clone https://github.com/sierraoliver/Youtube-To-Spotfiy-Converter.git
```

Move into the project directory:

```bash
cd Youtube-To-Spotfiy-Converter
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Create a `.env` file in the root directory and add:

```env
YOUTUBE_KEY=your_youtube_api_key
SPOTIFY_CLIENT_ID=your_client_id
SPOTIFY_CLIENT_SECRET=your_client_secret
SPOTIFY_REDIRECT_URI=http://127.0.0.1:8888/callback
```

Run the application:

```bash
python app.py
```
note: to run without in progress UI, use logic.py and run main(<insert youtube playlist URL>, <insert genre>) and make sure to uncomment last section of main function to add playlist to spotify acccount
------------------------------------------------------------------------------------
