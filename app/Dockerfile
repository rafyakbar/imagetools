# Menggunakan image Python official
FROM python:3.10-slim

# Install Tesseract OCR
RUN apt-get update && apt-get install -y tesseract-ocr

# Set working dir
WORKDIR /app

# Copy file requirements
COPY requirements.txt .

# Menginstal dependensi yang terdaftar di requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy semua file kode aplikasi ke dalam image
COPY . .

# Expose port FastAPI
EXPOSE 8000

# Command untuk menjalankan FastAPI menggunakan Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]