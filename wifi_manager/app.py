from flask import Flask, request, jsonify, render_template, send_file
import yt_dlp
import requests
from bs4 import BeautifulSoup
import os

app = Flask(__name__)

# Homepage
@app.route('/')
def home():
    return render_template('index.html')

# API: Fetch video info (thumbnail, formats)
@app.route('/api/info', methods=['POST'])
def get_video_info():
    url = request.json.get('url')
    
    try:
        ydl = yt_dlp.YoutubeDL({'quiet': True})
        info = ydl.extract_info(url, download=False)
        thumbnail = info.get('thumbnail', '')
        formats = info.get('formats', [])
    except Exception as e:
        thumbnail = fetch_thumbnail_via_og(url)
        formats = []

    return jsonify({'thumbnail': thumbnail, 'formats': formats})

# API: Download video
@app.route('/api/download')
def download_video():
    url = request.args.get('url')
    quality = request.args.get('quality', 'best')

    ydl_opts = {
        'format': quality,
        'outtmpl': 'downloads/%(title)s.%(ext)s',
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        filename = ydl.prepare_filename(info)
    
    return send_file(filename, as_attachment=True)

# Helper: Fallback thumbnail scraper
def fetch_thumbnail_via_og(url):
    try:
        res = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
        soup = BeautifulSoup(res.text, 'html.parser')
        meta_og_image = soup.find('meta', property='og:image')
        return meta_og_image['content'] if meta_og_image else ''
    except:
        return ''

if __name__ == '__main__':
    os.makedirs('downloads', exist_ok=True)
    app.run(debug=True)