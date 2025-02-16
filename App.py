from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
import yt_dlp
import tempfile
import os
import threading
import time

app = Flask(__name__)
CORS(app)

downloads = {}  # Dictionary لتتبع الملفات التي يتم تحميلها

def sanitize_filename(filename):
    return "video.mp4"

def download_and_save(video_url, download_id):
    """ تحميل الفيديو باستخدام yt-dlp وحفظه في مجلد مؤقت """
    temp_dir = tempfile.mkdtemp()
    ydl_opts = {
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        'outtmpl': os.path.join(temp_dir, '%(title)s.%(ext)s'),
        'quiet': True,
        'no_warnings': True,
        'cookies_from_browser': 'chrome'
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([video_url])

        filename = os.listdir(temp_dir)[0]
        file_path = os.path.join(temp_dir, filename)
        sanitized_name = sanitize_filename(filename)
        
        # حفظ المسار النهائي للتحميل
        downloads[download_id] = file_path

    except Exception as e:
        downloads[download_id] = f"error: {str(e)}"

@app.route('/')
def home():
    return "Backend is running successfully!"

@app.route('/download', methods=['POST'])
def download_video():
    data = request.json
    video_url = data.get('url')

    if not video_url:
        return jsonify({'error': 'No URL provided'}), 400

    download_id = str(int(time.time()))  # إنشاء ID فريد لكل تحميل
    downloads[download_id] = "Downloading"

    thread = threading.Thread(target=download_and_save, args=(video_url, download_id))
    thread.start()

    return jsonify({"message": "Download started", "download_id": download_id}), 202

@app.route('/status/<download_id>', methods=['GET'])
def check_status(download_id):
    if download_id not in downloads:
        return jsonify({'error': 'Invalid download ID'}), 404
    
    status = downloads[download_id]
    
    if "error" in status:
        return jsonify({'error': status}), 500
    elif status == "Downloading":
        return jsonify({'status': 'Downloading'}), 202
    else:
        return jsonify({'status': 'Completed', 'download_url': f"/file/{download_id}"}), 200

@app.route('/file/<download_id>', methods=['GET'])
def get_file(download_id):
    if download_id not in downloads or "error" in downloads[download_id] or downloads[download_id] == "Downloading":
        return jsonify({'error': 'File not ready or error occurred'}), 404

    file_path = downloads[download_id]
    return send_file(file_path, as_attachment=True, download_name="video.mp4", mimetype='video/mp4')

if __name__ == '__main__':
    app.run(debug=True)
