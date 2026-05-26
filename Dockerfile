# Utilizamos una imagen base ligera de Python para optimizar el rendimiento
FROM python:3.11-slim

# Establecemos el directorio de trabajo dentro del contenedor
WORKDIR /app

# Copiamos el archivo de dependencias primero para aprovechar la caché de Docker
COPY requirements.txt .

# Instalamos las dependencias necesarias
RUN pip install --no-cache-dir -r requirements.txt

# Copiamos el resto del código fuente al contenedor
COPY . .

# Exponemos el puerto estándar donde escucha la API
EXPOSE 8000

# Comando definitivo para iniciar el servidor
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
