# Usamos una imagen completa de Python para asegurar compatibilidad de librerías
FROM python:3.10

# Instalamos ffmpeg, libopus0 y herramientas necesarias
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libopus0 \
    && rm -rf /var/lib/apt/lists/*

# Establecemos nuestro directorio de trabajo
WORKDIR /app

# Primero copiamos los archivos de requerimientos para aprovechar el caché
COPY requirements.txt .

# Instalamos las dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Copiamos el resto del código del bot y la música (si ya la descargaste)
COPY . .

# Comando principal para iniciar el bot
CMD ["python", "bot.py"]
