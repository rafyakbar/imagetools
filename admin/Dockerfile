# Menggunakan image Python official
FROM python:3.10-slim

# Set working dir
WORKDIR /app

# Copy file requirements
COPY requirements.txt .

# Menginstal dependensi yang terdaftar di requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy semua file kode aplikasi ke dalam image
COPY . .

# Eksekusi file app.py ketika container dimulai
CMD ["python", "app.py"]