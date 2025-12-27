FROM python:3.11

# نصب FFmpeg و سایر وابستگی‌های سیستمی
RUN apt-get update && \
    apt-get install -y ffmpeg curl && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# آپدیت کردن پیپ
RUN pip install --upgrade pip

COPY requirements.txt .
# نصب وابستگی‌ها (به جز yt-dlp که جداگانه نصب می‌کنیم)
RUN pip install --no-cache-dir -r requirements.txt

# نصب آخرین نسخه yt-dlp مستقیماً از گیت‌هاب (بسیار مهم برای دور زدن بلاک)
RUN pip install --force-reinstall https://github.com/yt-dlp/yt-dlp/archive/master.zip

COPY . .
RUN mkdir -p temp_downloads

# افزایش تایم‌اوت به ۳۰۰ ثانیه
CMD gunicorn app:app --bind 0.0.0.0:$PORT --timeout 300
