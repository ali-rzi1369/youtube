from flask import Flask, request, send_file, jsonify, after_this_request
from flask_cors import CORS
import yt_dlp
import os
import uuid

# ایجاد اپلیکیشن Flask
app = Flask(__name__)
# فعال‌سازی CORS برای اجازه دادن به درخواست‌ها از فایل HTML شما
CORS(app)

# پوشه‌ای برای ذخیره موقت فایل‌ها
DOWNLOAD_FOLDER = 'temp_downloads'
if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)

@app.route('/download', methods=['GET'])
def download_video():
    # دریافت پارامترها از آدرس
    url = request.args.get('url')
    quality = request.args.get('quality', '720p') # پیش‌فرض 720p

    if not url:
        return jsonify({'error': 'لینک ویدئو وارد نشده است'}), 400

    try:
        # تبدیل فرمت کیفیت انتخابی (مثلاً 1080p) به عدد (1080)
        height_value = quality.replace('p', '')
        
        # تنظیم نام فایل یکتا برای جلوگیری از تداخل درخواست‌های همزمان
        unique_id = str(uuid.uuid4())
        
        # تنظیمات yt-dlp
        ydl_opts = {
            # فرمت: بهترین ویدئو با ارتفاع کمتر یا مساوی کیفیت درخواستی + بهترین صدا
            'format': f'bestvideo[height<={height_value}]+bestaudio/best[height<={height_value}]/best',
            # فرمت خروجی نهایی همیشه MP4 باشد
            'merge_output_format': 'mp4',
            # محل ذخیره فایل
            'outtmpl': f'{DOWNLOAD_FOLDER}/{unique_id}.%(ext)s',
            # خاموش کردن لاگ‌های اضافی
            'quiet': True,
            'no_warnings': True,
        }

        final_filename = None

        # شروع دانلود
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # استخراج اطلاعات ویدئو
            info = ydl.extract_info(url, download=True)
            
            # پیدا کردن مسیر فایل نهایی
            # نکته: اگرچه outtmpl دادیم، اما اکستنشن ممکن است تغییر کند
            # پس فایل را در پوشه پیدا می‌کنیم
            temp_filename = ydl.prepare_filename(info)
            # چون مرج به mp4 اجباری شده، اکستنشن نهایی mp4 است
            final_path = os.path.splitext(temp_filename)[0] + '.mp4'
            
            if os.path.exists(final_path):
                final_filename = final_path
            else:
                # اگر مرج لازم نبود و فایل اصلی دانلود شد
                final_filename = temp_filename

        # مسیر مطلق فایل برای ارسال
        abs_path = os.path.abspath(final_filename)
        video_title = info.get('title', 'video').replace('/', '_') # حذف کاراکترهای غیرمجاز

        # تابعی برای حذف فایل بعد از ارسال به کاربر (برای پر نشدن هارد سرور)
        @after_this_request
        def remove_file(response):
            try:
                if os.path.exists(abs_path):
                    os.remove(abs_path)
                    print(f"فایل موقت حذف شد: {abs_path}")
            except Exception as e:
                print(f"خطا در حذف فایل: {e}")
            return response

        # ارسال فایل به کاربر
        return send_file(
            abs_path, 
            as_attachment=True, 
            download_name=f"{video_title}_{quality}.mp4",
            mimetype='video/mp4'
        )

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'error': 'دانلود انجام نشد. لینک یا سرور مشکل دارد.'}), 500

if __name__ == '__main__':
    # اجرای سرور روی پورت 3000
    print("سرور روی پورت 3000 در حال اجراست...")
    app.run(debug=True, port=3000)