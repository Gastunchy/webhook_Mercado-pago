# Usar una imagen oficial de Python
FROM python:3.12

# Establecer el directorio de trabajo
WORKDIR /app

# Copiar archivos al contenedor
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código
COPY . .

# Exponer el puerto 8080
EXPOSE 8080

# Ejecutar la app
CMD ["python", "server.py"]
