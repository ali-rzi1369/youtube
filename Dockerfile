# استفاده از نسخه سبک پایتون
FROM python:3.9-slim

# نصب FFmpeg (حیاتی برای ترکیب صدا و تصویر)
RUN apt-get update && \
    apt-get install -y ffmpeg && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# تنظیم دایرکتوری کاری
WORKDIR /app

# کپی کردن فایل نیازمندی‌ها و نصب آن‌ها
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# کپی کردن کل پروژه به سرور
COPY . .

# ایجاد پوشه دانلود موقت
RUN mkdir -p temp_downloads

# دستور اجرای برنامه با Gunicorn (وب‌سرور قوی برای پروداکشن)
# Render پورت را به صورت متغیر محیطی $PORT ارسال می‌کند
CMD gunicorn app:app --bind 0.0.0.0:$PORT --timeout 120