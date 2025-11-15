import os
import logging
from flask import Flask, request, jsonify
from flask_cors import CORS
from ytmusicapi import YTMusic
from pytubefix import YouTube
import time

app = Flask(__name__)

# Enable CORS for all routes
CORS(app)

# Configure logging for production
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Request logging middleware
@app.before_request
def log_request_info():
    logger.info(f'{request.method} {request.url} - {request.remote_addr}')

def search_and_get_stream_fixed(song_name, artist_name=""):
    """
    Search YouTube Music and get ACTUAL streaming URL (handles signatureCipher)
    """
    start_time = time.time()
    
    # Initialize YouTube Music API with proper location
    ytmusic = YTMusic(language='en', location='IN')
    
    # Search for the song
    search_start = time.time()
    search_query = f"{song_name} {artist_name}".strip()
    
    try:
        search_results = ytmusic.search(search_query, filter="songs", limit=5)
        search_time = time.time() - search_start

        if not search_results:
            logger.error(f"No search results found for: {search_query}")
            return None
    except Exception as e:
        logger.error(f"Search failed for '{search_query}': {str(e)}")
        return None
    
    # Get the first result
    first_result = search_results[0]
    video_id = first_result['videoId']
    title = first_result['title']
    artists = ', '.join([artist['name'] for artist in first_result['artists']])
    
    # Use pytubefix to get actual streaming URL (handles cipher decryption)
    stream_start = time.time()
    
    try:
        # Create YouTube object with the video URL
        youtube_url = f"https://music.youtube.com/watch?v={video_id}"
        yt = YouTube(youtube_url)
        
        # Get audio streams only
        audio_streams = yt.streams.filter(only_audio=True).order_by('abr').desc()
        
        if audio_streams:
            best_audio = audio_streams.first()
            stream_url = best_audio.url  # pytubefix automatically decodes signatureCipher
            
            stream_time = time.time() - stream_start
            total_time = time.time() - start_time
            
            audio_formats = []
            for stream in audio_streams:
                audio_formats.append({
                    'itag': stream.itag,
                    'quality': stream.abr,
                    'bitrate': stream.bitrate,
                    'codec': stream.mime_type,
                    'url': stream.url,
                    'filesize': stream.filesize,
                })
            
            return {
                'title': title,
                'artists': artists,
                'video_id': video_id,
                'stream_url': stream_url,
                'duration': yt.length,
                'thumbnail': yt.thumbnail_url,
                'quality': best_audio.abr,
                'bitrate': best_audio.bitrate,
                'codec': best_audio.mime_type,
                'all_formats': audio_formats,
                'search_time': search_time,
                'stream_time': stream_time,
                'total_time': total_time,
            }
    
    except Exception as e:
        return None
    
    return None

def get_stream_by_id(video_id):
    """
    Get streaming data and all audio formats for a specific video ID
    """
    try:
        youtube_url = f"https://music.youtube.com/watch?v={video_id}"
        yt = YouTube(youtube_url)
        
        audio_streams = yt.streams.filter(only_audio=True)
        
        if not audio_streams:
            return None
        
        best_audio = audio_streams.order_by('abr').desc().first()
        
        audio_formats = []
        for stream in audio_streams:
            audio_formats.append({
                'itag': stream.itag,
                'quality': stream.abr,
                'bitrate': stream.bitrate,
                'codec': stream.mime_type,
                'url': stream.url,
                'filesize': stream.filesize,
            })
        
        return {
            'video_id': video_id,
            'title': yt.title,
            'duration': yt.length,
            'thumbnail': yt.thumbnail_url,
            'best_stream': {
                'url': best_audio.url,
                'quality': best_audio.abr,
                'bitrate': best_audio.bitrate,
                'codec': best_audio.mime_type,
                'filesize': best_audio.filesize,
            },
            'all_formats': audio_formats
        }
    
    except Exception as e:
        return None
def get_dash_audio(video_id):
    """
    Get DASH audio streams for a specific video ID
    """
    try:
        youtube_url = f"https://music.youtube.com/watch?v={video_id}"
        yt = YouTube(youtube_url)
        
        # Try to get DASH streams (adaptive audio)
        dash_audio_streams = yt.streams.filter(only_audio=True, adaptive=True)
        if not dash_audio_streams:
            # Fallback: try progressive streams that might be DASH-like
            dash_audio_streams = yt.streams.filter(only_audio=True)

        if not dash_audio_streams:
            logger.error(f"No DASH audio streams found for video: {video_id}")
            return None
        
        dash_formats = []
        for stream in dash_audio_streams:
            dash_formats.append({
                'itag': stream.itag,
                'quality': stream.abr,
                'bitrate': stream.bitrate,
                'codec': stream.mime_type,
                'url': stream.url,
                'filesize': stream.filesize,
            })
        
        return {
            'video_id': video_id,
            'title': yt.title,
            'duration': yt.length,
            'thumbnail': yt.thumbnail_url,
            'dash_audio_streams': dash_formats
        }
    
    except Exception as e:
        return None

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint for load balancers and monitoring"""
    return jsonify({
        "status": "healthy",
        "timestamp": int(time.time()),
        "service": "yt-music-python-restapi"
    })


@app.route('/search_and_stream', methods=['POST'])
def search_and_stream():
    data = request.get_json()
    if not data or 'song_name' not in data:
        return jsonify({'error': 'Please provide song_name in JSON body'}), 400
    
    song_name = data['song_name']
    artist_name = data.get('artist_name', '')
    
    result = search_and_get_stream_fixed(song_name, artist_name)
    if result:
        return jsonify(result)
    else:
        return jsonify({'error': 'Song not found'}), 404

@app.route('/stream/<video_id>', methods=['GET'])
def stream_by_id(video_id):
    result = get_stream_by_id(video_id)
    if result:
        return jsonify(result)
    else:
        return jsonify({'error': 'Video not found or no audio streams available'}), 404
@app.route('/dash/<video_id>', methods=['GET'])
def dash_audio(video_id):
    result = get_dash_audio(video_id)
    if result:
        return jsonify(result)
    else:
        return jsonify({'error': 'Video not found or no DASH audio streams available'}), 404

# For production deployment with WSGI server like gunicorn
# Run with: gunicorn --bind 0.0.0.0:8000 app:app
# Or use the app object directly if needed

if __name__ == '__main__':
    # For local testing only; in production, use WSGI server
    host = os.getenv('HOST', '0.0.0.0')
    port = int(os.getenv('PORT', 5000))
    app.run(host=host, port=port, debug=False)
