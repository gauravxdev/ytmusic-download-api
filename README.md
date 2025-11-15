# YouTube Music Python REST API

This is a Python Flask REST API for searching YouTube Music and getting streaming URLs. It uses `ytmusicapi` for searching and `pytubefix` for handling streaming URLs with signature cipher decryption.

## Installation

1. Navigate to the project directory:
   ```bash
   cd yt_music_python_restapi
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Running the API

### Development
Start the Flask development server:
```bash
python app.py
```

The API will run on `http://localhost:5000` by default.

### Production
For production deployment on platforms like Render, Railway, or Heroku:

**Start Command:**
```
gunicorn app:app
```

The app automatically uses the `PORT` environment variable set by the hosting platform.

**Environment Variables:**
- `PORT` - Automatically set by hosting platform
- `HOST` - Defaults to `0.0.0.0`

**Health Check:**
The `/health` endpoint can be used for monitoring and health checks.

## Endpoints

### 1. Search and Get Streaming URL
**Endpoint:** `POST /search_and_stream`

Searches for a song on YouTube Music and returns the best quality streaming URL along with metadata and all available formats.

**Request:**
- Method: POST
- Content-Type: application/json
- Body:
  ```json
  {
    "song_name": "Song Title",
    "artist_name": "Artist Name"
  }
  ```

**Response (200 OK):**
```json
{
  "title": "Song Title",
  "artists": "Artist Name",
  "video_id": "VIDEOID12341234",
  "stream_url": "https://...",
  "duration": 240,
  "thumbnail": "https://...",
  "quality": "128kbps",
  "bitrate": 128000,
  "codec": "audio/webm",
  "all_formats": [...],
  "search_time": 2.15,
  "stream_time": 1.23,
  "total_time": 3.38
}
```

### 2. Get Streaming URL by Video ID
**Endpoint:** `GET /stream/<video_id>`

Gets streaming URLs and audio formats for a specific YouTube video ID.

**Request:**
- Method: GET
- URL: `http://localhost:5000/stream/VIDEOID12341234`

**Response (200 OK):**
```json
{
  "video_id": "VIDEOID12341234",
  "title": "Song Title",
  "duration": 240,
  "thumbnail": "https://...",
  "best_stream": {
    "url": "https://...",
    "quality": "128kbps",
    "bitrate": 128000,
    "codec": "audio/webm",
    "filesize": 3840000
  },
  "all_formats": [...]
}
```
### 3. Get DASH Audio Streams
**Endpoint:** `GET /dash/<video_id>`

Gets DASH audio streams for a specific YouTube video ID. DASH streams allow adaptive bitrate streaming.

**Request:**
- Method: GET
- URL: `http://localhost:5000/dash/VIDEOID12341234`

**Response (200 OK):**
```json
{
  "video_id": "VIDEOID12341234",
  "title": "Song Title",
  "duration": 240,
  "thumbnail": "https://...",
  "dash_audio_streams": [
    {
      "itag": 140,
      "quality": "128kbps",
      "bitrate": 128000,
      "codec": "audio/mp4",
      "url": "https://...",
      "filesize": 3840000
    },
    ...
  ]
}
```

### 3. Get DASH Audio Streams

1. Create a new GET request in Postman.
2. Set method to **GET**.
3. Enter URL: `http://localhost:5000/dash/YOUR_VIDEO_ID`
   (Replace YOUR_VIDEO_ID with an actual video ID, e.g., `Ljz0tdAJL-4`)
4. Click **Send**. You should receive DASH audio streams information.


## Testing with Postman

### 1. Search and Get Streaming URL

1. Open Postman and create a new request.
2. Set method to **POST**.
3. Enter URL: `http://localhost:5000/search_and_stream`
4. Go to Headers tab:
   - Key: `Content-Type`
   - Value: `application/json`
5. Go to Body tab:
   - Select raw
   - Select JSON
   - Enter:
     ```json
     {
       "song_name": "Khuda bhi Jab",
       "artist_name": "Ankit Tiwari"
     }
     ```
6. Click **Send**. You should receive a JSON response with the streaming URL and metadata.

### 2. Get Streaming URL by Video ID

1. Create a new GET request in Postman.
2. Set method to **GET**.
3. Enter URL: `http://localhost:5000/stream/YOUR_VIDEO_ID`
   (Replace YOUR_VIDEO_ID with an actual video ID, e.g., `Ljz0tdAJL-4`)
4. Click **Send**. You should receive streaming URLs and format information.

## Dependencies

- Flask: Web framework
- ytmusicapi: YouTube Music API for searching
- pytubefix: Modified pytube for handling YouTube streams including signature cipher

## Notes

- The API returns working streaming URLs that can be used directly for audio playback.
- All available audio formats are included in the response for more advanced use cases.
- Performance metrics (search time, stream extraction time) are included in search responses.
