import yt_dlp  # Import yt-dlp to handle YouTube streams

def get_youtube_stream_url(youtube_url):
    """Fetch the YouTube stream URL using yt-dlp."""
    ydl_opts = {
        'format': 'best[height<=480]',  # 'best' will automatically choose the best available format for normal videos and live streams
        'noplaylist': True,
        'quiet': True,
        'cookiefile': 'cookies.txt',  # Path to your cookies file
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(youtube_url, download=False)
        
        # Check if this is a live stream or a regular video
        if 'is_live' in info_dict and info_dict['is_live']:
            stream_url = info_dict.get('url', None)  # For live streams
        else:
            # For normal videos, we return the best available stream
            formats = info_dict.get('formats', [])
            if formats:
                stream_url = formats[-1].get('url')  # The best available format at the end of the list
            else:
                raise Exception("No stream URL found for the video.")
    
    return stream_url