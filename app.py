from flask import Flask, request, send_file, jsonify, after_this_request
from flask_cors import CORS
import yt_dlp
import os
import uuid

app = Flask(__name__)
CORS(app)

DOWNLOAD_FOLDER = 'temp_downloads'
if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)

@app.route('/download', methods=['GET'])
def download_video():
    url = request.args.get('url')
    quality = request.args.get('quality', '720p')

    if not url:
        return jsonify({'error': 'لینک ویدئو وارد نشده است'}), 400

    try:
        height_value = quality.replace('p', '')
        unique_id = str(uuid.uuid4())
        
        # تنظیمات جدید برای جلوگیری از بلاک شدن
        ydl_opts = {
            'format': f'bestvideo[height<={height_value}]+bestaudio/best[height<={height_value}]/best',
            'merge_output_format': 'mp4',
            'outtmpl': f'{DOWNLOAD_FOLDER}/{unique_id}.%(ext)s',
            'quiet': True,
            'no_warnings': True,
            # تنظیمات مهم ضد شناسایی:
            'nocheckcertificate': True,
            'geo_bypass': True,
            'source_address': '0.0.0.0',
            # شبیه‌سازی درخواست از طریق کلاینت اندروید (معمولاً کمتر بلاک می‌شود)
            'extractor_args': {
                'youtube': {
                    'player_client': ['android', 'ios']
                }
            },
            # اضافه کردن هدرهای مرورگر واقعی
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Mobile Safari/537.36',
                'Accept-Language': 'en-US,en;q=0.9',
            }
        }

        final_filename = None

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            try:
                info = ydl.extract_info(url, download=True)
            except yt_dlp.utils.DownloadError as e:
                # اگر باز هم خطا داد، پیام دقیق‌تری برگردانیم
                print(f"YouTube DL Error: {e}")
                if "Sign in" in str(e) or "unavailable" in str(e):
                    return jsonify({'error': 'سرور توسط یوتیوب محدود شده است. لطفاً دقایقی دیگر تلاش کنید.'}), 403
                raise e

            temp_filename = ydl.prepare_filename(info)
            final_path = os.path.splitext(temp_filename)[0] + '.mp4'
            
            if os.path.exists(final_path):
                final_filename = final_path
            else:
                final_filename = temp_filename

        abs_path = os.path.abspath(final_filename)
        # ایمن‌سازی نام فایل برای دانلود
        video_title = "".join([c for c in info.get('title', 'video') if c.isalnum() or c in (' ', '-', '_')]).strip()

        @after_this_request
        def remove_file(response):
            try:
                if os.path.exists(abs_path):
                    os.remove(abs_path)
            except Exception as e:
                print(f"Error removing file: {e}")
            return response

        return send_file(
            abs_path, 
            as_attachment=True, 
            download_name=f"{video_title}_{quality}.mp4",
            mimetype='video/mp4'
        )

    except Exception as e:
        print(f"General Error: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=3000)
