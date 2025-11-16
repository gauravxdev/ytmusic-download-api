from flask import Flask, request, jsonify
from flask_cors import CORS
from ytmusicapi import YTMusic
from pytubefix import YouTube
import logging
import time

app = Flask(__name__)
CORS(app)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    ytmusic = YTMusic(language='en', location='IN')
except Exception as e:
    logger.error(f"YTMusic initialization failed: {str(e)}")
    ytmusic = None

def yt_search(song_name, artist_name=""):
    if not ytmusic:
        return {"error": "YTMusic service unavailable"}, 503
    query = f"{song_name} {artist_name}".strip()
    try:
        results = ytmusic.search(query, filter="songs", limit=5)
        if not results:
            return {"error": "No results found"}, 404
        return results
    except Exception as e:
        logger.error(f"Search error: {str(e)}")
        return {"error": "Search failed", "details": str(e)}, 500

def search_and_get_stream(song_name, artist_name=""):
    results = yt_search(song_name, artist_name)
    if isinstance(results, tuple):  # error case from yt_search
        return results[0], results[1]
    first = results[0]
    video_id = first.get('videoId')
    if not video_id:
        return {"error": "No videoId found"}, 404
    try:
        yt_obj = YouTube(f"https://music.youtube.com/watch?v={video_id}")
        audio_streams = yt_obj.streams.filter(only_audio=True).order_by('abr').desc()
        if not audio_streams:
            return {"error": "No audio stream"}, 404
        best_audio = audio_streams.first()
        return {
            "title": yt_obj.title,
            "artists": ', '.join([a.get('name') for a in first.get('artists', [])]),
            "video_id": video_id,
            "stream_url": best_audio.url,
            "thumbnail": yt_obj.thumbnail_url,
            "quality": best_audio.abr,
            "bitrate": best_audio.bitrate,
            "codec": best_audio.mime_type,
            "duration": yt_obj.length,
        }
    except Exception as e:
        logger.error(f"Stream error: {str(e)}")
        return {"error": "Stream failed", "details": str(e)}, 500

def validate_and_convert_video_id(video_id):
    if not video_id or len(video_id) < 10:
        return None
    if len(video_id) == 11 and video_id.replace('_', '').replace('-', '').isalnum():
        return video_id
    if video_id.startswith('MUSIC_VIDEO_ID_'):
        clean_id = video_id.replace('MUSIC_VIDEO_ID_', '')
        if len(clean_id) == 11:
            return clean_id
    logger.warning(f"Potentially invalid video ID format: {video_id}")
    return video_id

def get_stream_by_id(video_id):
    clean_video_id = validate_and_convert_video_id(video_id)
    if not clean_video_id:
        return {"error": "Invalid video ID format", "code": "INVALID_ID"}, 400
    urls_to_try = [
        f"https://music.youtube.com/watch?v={clean_video_id}",
        f"https://www.youtube.com/watch?v={clean_video_id}"
    ]
    yt = None
    for url in urls_to_try:
        try:
            yt = YouTube(url)
            if yt.title and yt.title != "YouTube":
                break
        except Exception as url_error:
            logger.warning(f"Failed to load from {url}: {str(url_error)}")
    if not yt or not yt.title or yt.title == "YouTube":
        return {"error": "Video not found or not accessible", "code": "VIDEO_NOT_FOUND"}, 404
    audio_streams = yt.streams.filter(only_audio=True)
    if not audio_streams:
        return {"error": "No audio streams available for this video", "code": "NO_AUDIO_STREAMS"}, 404
    best_audio = audio_streams.order_by('abr').desc().first()
    audio_formats = [{
        "itag": stream.itag,
        "quality": stream.abr,
        "bitrate": stream.bitrate,
        "codec": stream.mime_type,
        "url": stream.url,
        "filesize": stream.filesize,
    } for stream in audio_streams]
    return {
        "video_id": clean_video_id,
        "title": yt.title,
        "duration": yt.length,
        "thumbnail": yt.thumbnail_url,
        "best_stream": {
            "url": best_audio.url,
            "quality": best_audio.abr,
            "bitrate": best_audio.bitrate,
            "codec": best_audio.mime_type,
            "filesize": best_audio.filesize,
        },
        "all_formats": audio_formats
    }, 200

def get_dash_audio(video_id):
    clean_video_id = validate_and_convert_video_id(video_id)
    if not clean_video_id:
        return {"error": "Invalid video ID format", "code": "INVALID_ID"}, 400
    urls_to_try = [
        f"https://music.youtube.com/watch?v={clean_video_id}",
        f"https://www.youtube.com/watch?v={clean_video_id}"
    ]
    yt = None
    for url in urls_to_try:
        try:
            yt = YouTube(url)
            if yt.title and yt.title != "YouTube":
                break
        except Exception as url_error:
            logger.warning(f"Failed to load from {url}: {str(url_error)}")
    if not yt or not yt.title or yt.title == "YouTube":
        return {"error": "Video not found or not accessible", "code": "VIDEO_NOT_FOUND"}, 404
    dash_audio_streams = yt.streams.filter(only_audio=True, adaptive=True)
    if not dash_audio_streams:
        dash_audio_streams = yt.streams.filter(only_audio=True)
    if not dash_audio_streams:
        return {"error": "No audio streams available for this video", "code": "NO_AUDIO_STREAMS"}, 404
    dash_formats = [{
        "itag": stream.itag,
        "quality": stream.abr,
        "bitrate": stream.bitrate,
        "codec": stream.mime_type,
        "url": stream.url,
        "filesize": stream.filesize,
    } for stream in dash_audio_streams]
    return {
        "video_id": clean_video_id,
        "title": yt.title,
        "duration": yt.length,
        "thumbnail": yt.thumbnail_url,
        "dash_audio_streams": dash_formats
    }, 200

@app.route('/searchandstream', methods=['POST'])
def searchandstream_route():
    data = request.get_json(force=True)
    song = data.get('song_name')
    artist = data.get('artist_name', '')
    if not song:
        return jsonify({"error": "Provide song_name"}), 400
    result = search_and_get_stream(song, artist)
    status = 200 if isinstance(result, dict) else result[1]
    output = result if isinstance(result, dict) else result[0]
    return jsonify(output), status

@app.route('/search', methods=['POST'])
def search_route():
    data = request.get_json(force=True)
    song = data.get('song_name')
    artist = data.get('artist_name', '')
    if not song:
        return jsonify({"error": "Provide song_name"}), 400
    results = yt_search(song, artist)
    if isinstance(results, tuple):
        return jsonify(results[0]), results[1]
    cleaned = [{
        "title": r.get("title"),
        "video_id": r.get("videoId"),
        "artists": ', '.join([a.get("name") for a in r.get("artists", [])]),
        "thumbnail": r.get("thumbnails", [{}])[-1].get("url", "")
    } for r in results]
    return jsonify({"results": cleaned})

@app.route('/stream/<video_id>', methods=['GET'])
def stream_by_id_route(video_id):
    result, status = get_stream_by_id(video_id)
    return jsonify(result), status

@app.route('/dash/<video_id>', methods=['GET'])
def dash_audio_route(video_id):
    result, status = get_dash_audio(video_id)
    return jsonify(result), status

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        "status": "healthy",
        "timestamp": int(time.time()),
        "service": "yt-music-python-restapi"
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
