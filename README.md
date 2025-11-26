# YouTube Music Python REST API

A Flask-based REST API that provides comprehensive endpoints for searching and streaming YouTube Music content. This API combines `ytmusicapi` for searching and `pytubefix` for streaming functionality with signature cipher decryption.

## Features

- **Song Search**: Search YouTube Music database for songs and artists
- **Stream Extraction**: Get direct streaming URLs for audio playback
- **Multiple Format Support**: Access various audio formats and qualities
- **DASH Streaming**: Adaptive bitrate streaming support
- **Video ID Processing**: Handles standard YouTube IDs and YouTube Music prefixed IDs
- **Bot Detection Handling**: Automatic PO token generation as fallback
- **CORS Enabled**: Ready for frontend integration

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
- `PO_TOKEN` - (Optional) PO Token for bypassing YouTube bot detection. See pytubefix documentation for how to obtain.

## Endpoints

### 1. Search and Get Streaming URL
**Endpoint:** `POST /searchandstream`

Searches for a song on YouTube Music and returns the best quality streaming URL along with metadata and all available formats.

**Request:**
- Method: POST
- Content-Type: application/json
- Body:
  ```json
  {
    "song_name": "Song Title",
    "artist_name": "Artist Name (optional)"
  }
  ```

**Response (200 OK):**
```json
{
  "title": "Song Title",
  "artists": "Artist Name",
  "video_id": "VIDEOID12341234",
  "stream_url": "https://...",
  "thumbnail": "https://...",
  "quality": "128kbps",
  "bitrate": 128000,
  "codec": "audio/webm",
  "duration": 240,
  "all_formats": [
    {
      "itag": 140,
      "quality": "128kbps",
      "bitrate": 128000,
      "codec": "audio/mp4",
      "url": "https://...",
      "filesize": 3840000
    }
  ]
}
```

**Error Responses:**
- `400 Bad Request` - Missing song_name parameter
- `404 Not Found` - No results found or no video ID
- `429 Too Many Requests` - Bot detection triggered
- `500 Internal Server Error` - Search or stream extraction failed
- `503 Service Unavailable` - YTMusic service unavailable

### 2. Search Only
**Endpoint:** `POST /search`

Searches for songs on YouTube Music and returns clean search results without streaming information.

**Request:**
- Method: POST
- Content-Type: application/json
- Body:
  ```json
  {
    "song_name": "Song Title",
    "artist_name": "Artist Name (optional)"
  }
  ```

**Response (200 OK):**
```json
{
  "results": [
    {
      "title": "Song Title",
      "video_id": "VIDEOID12341234",
      "artists": "Artist Name",
      "thumbnail": "https://..."
    }
  ]
}
```

**Error Responses:**
- `400 Bad Request` - Missing song_name parameter
- `404 Not Found` - No results found
- `500 Internal Server Error` - Search failed
- `503 Service Unavailable` - YTMusic service unavailable

### 3. Get Streaming URL by Video ID
**Endpoint:** `GET /stream/<video_id>`

Gets streaming URLs and audio formats for a specific YouTube video ID. Supports both standard YouTube IDs and YouTube Music prefixed IDs.

**Request:**
- Method: GET
- URL: `http://localhost:5000/stream/VIDEOID12341234` or `http://localhost:5000/stream/MUSIC_VIDEO_ID_dQw4w9WgXcQ`

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
  "all_formats": [
    {
      "itag": 140,
      "quality": "128kbps",
      "bitrate": 128000,
      "codec": "audio/mp4",
      "url": "https://...",
      "filesize": 3840000
    }
  ]
}
```

**Error Responses:**
- `400 Bad Request` - Invalid video ID format
- `404 Not Found` - Video not found or no audio streams available
- `500 Internal Server Error` - Stream extraction failed

### 4. Get DASH Audio Streams
**Endpoint:** `GET /dash/<video_id>`

Gets DASH audio streams for a specific YouTube video ID. DASH streams allow adaptive bitrate streaming for better quality adaptation.

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
    }
  ]
}
```

**Error Responses:**
- `400 Bad Request` - Invalid video ID format
- `404 Not Found` - Video not found or no audio streams available
- `500 Internal Server Error` - Stream extraction failed

### 5. Health Check
**Endpoint:** `GET /health`

Health check endpoint for monitoring API status and service availability.

**Request:**
- Method: GET
- URL: `http://localhost:5000/health`

**Response (200 OK):**
```json
{
  "status": "healthy",
  "timestamp": 1637890123,
  "service": "yt-music-python-restapi"
}
```

## Video ID Formats

The API accepts various YouTube video ID formats:
- Standard YouTube video IDs: `dQw4w9WgXcQ`
- YouTube Music prefixed IDs: `MUSIC_VIDEO_ID_dQw4w9WgXcQ`
- The API automatically validates and converts IDs to the correct format

## Error Handling

The API provides detailed error responses with appropriate HTTP status codes:

- **400 Bad Request**: Missing required parameters or invalid video ID format
- **404 Not Found**: No search results or video not accessible
- **429 Too Many Requests**: Bot detection triggered, try again later
- **500 Internal Server Error**: Stream extraction or processing failed
- **503 Service Unavailable**: YTMusic service unavailable

## Testing with Postman

### 1. Search and Stream Combined
1. Create a new POST request in Postman
2. Set URL: `http://localhost:5000/searchandstream`
3. Go to Headers tab, add:
   - Key: `Content-Type`, Value: `application/json`
4. Go to Body tab, select raw and JSON, enter:
   ```json
   {
     "song_name": "Khuda bhi Jab",
     "artist_name": "Ankit Tiwari"
   }
   ```
5. Click Send

### 2. Search Only
1. Create a new POST request in Postman
2. Set URL: `http://localhost:5000/search`
3. Configure headers and body the same as above
4. Click Send

### 3. Get Stream by Video ID
1. Create a new GET request in Postman
2. Set URL: `http://localhost:5000/stream/Ljz0tdAJL-4`
3. Click Send

### 4. Get DASH Audio Streams
1. Create a new GET request in Postman
2. Set URL: `http://localhost:5000/dash/Ljz0tdAJL-4`
3. Click Send

### 5. Health Check
1. Create a new GET request in Postman
2. Set URL: `http://localhost:5000/health`
3. Click Send

## Dependencies

- **Flask**: Web framework for building the REST API
- **flask-cors**: Cross-Origin Resource Sharing support
- **ytmusicapi**: YouTube Music API for searching songs and artists
- **pytubefix**: Modified pytube for handling YouTube streams including signature cipher decryption

## Key Features

- **Working Streaming URLs**: All returned URLs can be used directly for audio playback
- **Multiple Format Support**: Returns all available audio formats for advanced use cases
- **Performance Metrics**: Includes timing information in search responses
- **Bot Detection Handling**: Automatic fallback for YouTube's bot detection
- **Video ID Validation**: Automatic conversion of various YouTube ID formats
- **DASH Streaming Support**: Adaptive bitrate streaming capabilities
- **Health Monitoring**: Built-in health check endpoint for deployment monitoring

## Notes

- The API returns direct streaming URLs that can be used immediately for audio playback
- Search functionality may be limited on some cloud hosting platforms due to YouTube API restrictions
- For production deployments, consider setting the `PO_TOKEN` environment variable to bypass bot detection
- The `/stream/<video_id>` endpoint works reliably for known video IDs even when search is restricted
