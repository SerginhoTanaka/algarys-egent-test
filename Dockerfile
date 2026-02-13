FROM python:3.12-slim

WORKDIR /app

# Instalar dependências do sistema necessárias para PDF processing
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    wget \
    git \
    libxcb1 \
    libx11-6 \
    libxrender1 \
    libxext6 \
    libssl-dev \
    libffi-dev \
    libc6 \
    libpoppler-cpp0 \
    libpoppler82 \
    tesseract-ocr \
    ghostscript \
    libopenjp2-7 \
    libtiff6 \
    libjpeg62-turbo \
    zlib1g \
    libfreetype6 \
    fontconfig \
    libexpat1 \
    libglib2.0-0 \
    libgio2.0-cil \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements
COPY requirements.txt .

# Instalar Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código da aplicação
COPY . .

# Criar diretórios necessários
RUN mkdir -p data/raw/staged/chroma

# Expor portas
EXPOSE 8000 8501

# Default é a API, mas pode ser sobrescrito
CMD ["uvicorn", "src.app.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
