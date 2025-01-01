from fastapi import FastAPI, UploadFile, File, Form, HTTPException
import os
import uuid
from celery_tasks import compress_image_task

app = FastAPI(
    title="ImageTools dengan Celery & RabbitMQ"
)

# Konfigurasi RabbitMQ
RABBITMQ_HOST = os.getenv('RABBITMQ_HOST', 'rabbitmq')
RABBITMQ_USER = os.getenv('RABBITMQ_USER', 'guest')
RABBITMQ_PASS = os.getenv('RABBITMQ_PASS', 'guest')

# Membuat direktori uploaded jika belum ada
UPLOAD_DIR = "uploaded"
os.makedirs(UPLOAD_DIR, exist_ok=True)


async def save_file(upload_dir: str, file: UploadFile):
    # Mendapatkan ekstensi file
    file_extension = file.filename.split('.')[-1]
    # Membuat nama file dengan UUID
    file_name = f"{uuid.uuid4()}.{file_extension}"
    # Membuat path lengkap
    full_path = os.path.join(upload_dir, file_name)

    # Menyimpan file
    with open(full_path, "wb") as f:
        f.write(await file.read())

    return full_path

@app.get("/")
def index():
    return {"status": "ok"}

@app.post("/compress/")
async def compress_image(file: UploadFile = File(...), compression_rate: int = Form(...)):
    # Validasi file gambar
    if not file.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="File must be an image.")

    # Validasi compression_rate
    if not (1 <= compression_rate <= 100):
        raise HTTPException(status_code=400, detail="Compression rate must be an integer between 1 and 100.")

    # Membuat direktori untuk compress_service jika belum ada
    compress_dir = os.path.join(UPLOAD_DIR, "compress_service")
    os.makedirs(compress_dir, exist_ok=True)

    # Simpan file di dalam folder compress_service
    file_location = await save_file(compress_dir, file)

    # Memanggil tugas Celery untuk mengompres gambar
    compress_image_task.delay(file_location, compression_rate)

    return {
        "message": "Task execution started",
        "file_location": file_location
    }