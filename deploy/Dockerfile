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

ENV FLASK_APP=OCR_app.py 
ENV FLASK_ENV=production

RUN pip install --no-cache-dir gunicorn
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:3001", "OCR_app:app"]