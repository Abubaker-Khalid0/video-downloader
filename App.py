from flask import Flask, request, send_file
from flask_cors import CORS
import yt_dlp
import tempfile
import os

app = Flask(__name__)
CORS(app)

def sanitize_filename(filename):
    # Add your sanitization logic here
    return "video.mp4"

@app.route('/')
def home():
    return "Backend is running successfully!"

@app.route('/download', methods=['POST'])
def download_video():
    data = request.json
    video_url = data.get('url')
    
    if not video_url:
        return {'error': 'No URL provided'}, 400

    ydl_opts = {
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        'outtmpl': '%(title)s.%(ext)s',
        'quiet': True,
        'no_warnings': True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=False)
            temp_dir = tempfile.mkdtemp()
            ydl_opts['outtmpl'] = os.path.join(temp_dir, '%(title)s.%(ext)s')
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([video_url])
            
            filename = os.listdir(temp_dir)[0]
            file_path = os.path.join(temp_dir, filename)
            sanitized_name = sanitize_filename(filename)
            
            return send_file(
                file_path,
                as_attachment=True,
                download_name=sanitized_name,
                mimetype='video/mp4'
            )

    except Exception as e:
        print(f"Error: {str(e)}")
        return {'error': str(e)}, 500


if __name__ == '__main__':
    app.run(debug=True)