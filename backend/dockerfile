# Imagen base ligera
FROM python:3.11-slim

# Directorio de trabajo
WORKDIR /app

# Instalar dependencias
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código fuente
COPY . .

# Exponer el puerto de su aplicación (ajuste si es necesario)
EXPOSE 8000

# Comando de ejecución (ajuste "src/main.py" según su archivo principal)
CMD ["python", "src/main.py"]
