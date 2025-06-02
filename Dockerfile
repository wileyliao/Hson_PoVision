FROM python:3.10

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    build-essential \
    cmake

# Copy requirements and install Python dependencies
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt
RUN pip install --no-cache-dir paddlepaddle-gpu==3.0.0 -i https://www.paddlepaddle.org.cn/packages/stable/cu118/
RUN ln -snf /usr/share/zoneinfo/Asia/Taipei /etc/localtime && echo "Asia/Taipei" > /etc/timezone

ENV FLASK_APP=OCR_app.py
ENV FLASK_ENV=production

CMD ["gunicorn", "-w", "1", "-b", "0.0.0.0:3001", "OCR_app:app", "--log-level=debug", "--access-logfile=-", "--error-logfile=-"]
