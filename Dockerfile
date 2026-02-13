FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    libxcb1 \
    libx11-6 \
    libxrender1 \
    libxext6 \
    libglib2.0-0 \
    libexpat1 \
    libfreetype6 \
    fontconfig \
    libgl1 \
    libglx-mesa0 \
    libopengl0 \
    libglu1-mesa \
    curl \
    wget \
    git \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p data/raw data/staged data/chroma

EXPOSE 8000

CMD ["uvicorn", "src.app.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
