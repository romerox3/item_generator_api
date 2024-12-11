FROM python:3.10

ENV DIFFUSION_MODEL=animate-diff

WORKDIR /app

# Instalar dependencias del sistema necesarias para OpenCV y otras bibliotecas
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Crear el directorio de imágenes
RUN mkdir -p /app/images

# Copiar los archivos de configuración de Poetry
COPY pyproject.toml poetry.lock* entrypoint.sh ./

# Instalar Poetry y las dependencias del proyecto
RUN pip3 install poetry && \
    poetry config virtualenvs.create false && \
    poetry install --no-dev

# Instalar PyTorch y dependencias relacionadas
RUN pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

# Copiar el resto del código
COPY . .

# Comando para ejecutar la aplicación
CMD ["python", "app.py"]