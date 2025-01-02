from fastapi import FastAPI, UploadFile, File, Form, HTTPException
import os
import uuid
from celery_tasks import compress_image_task, upscale_image_task, extract_text_task
from datetime import datetime
import pytz

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

    # Mendapatkan waktu saat ini
    now = datetime.now(pytz.timezone('Asia/Jakarta'))
    timestamp = now.strftime("%Y-%m-%d_%H-%M-%S")

    # Membuat nama file dengan format yang diinginkan
    file_name = f"{timestamp}_{uuid.uuid4()}.{file_extension}"

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

    # Memanggil celery task untuk mengompres gambar menggunakan apply_async
    compress_image_task.apply_async(
        args=[file_location, compression_rate],
        routing_key='imagetools.compress'
    )

    return {
        "message": "Task execution started",
        "file_location": file_location
    }

@app.post("/upscale/")
async def upscale_image(file: UploadFile = File(...), scale_factor: float = Form(...)):
    # Validasi file gambar
    if not file.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="File must be an image.")

    # Validasi scale_factor
    if scale_factor <= 1:
        raise HTTPException(status_code=400, detail="Scale factor must be greater than 1.")

    # Membuat direktori untuk upscale_service jika belum ada
    upscale_dir = os.path.join(UPLOAD_DIR, "upscale_service")
    os.makedirs(upscale_dir, exist_ok=True)

    # Simpan file di dalam folder upscale_service
    file_location = await save_file(upscale_dir, file)

    # Memanggil celery task untuk mengubah ukuran gambar menggunakan apply_async
    upscale_image_task.apply_async(
        args=[file_location, scale_factor],
        routing_key='imagetools.upscale'
    )

    return {
        "message": "Task execution started",
        "file_location": file_location
    }

@app.post("/extract-text/")
async def extract_text(file: UploadFile = File(...)):
    # Validasi file gambar
    if not file.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="File must be an image.")

    # Membuat direktori untuk extract_text_service jika belum ada
    extract_text_dir = os.path.join(UPLOAD_DIR, "extract_service")
    os.makedirs(extract_text_dir, exist_ok=True)

    # Simpan file di dalam folder extract_text_service
    file_location = await save_file(extract_text_dir, file)

    # Memanggil celery task untuk mengekstrak teks menggunakan apply_async
    extract_text_task.apply_async(
        args=[file_location],
        routing_key='imagetools.extract'
    )

    return {
        "message": "Task execution started",
        "file_location": file_location
    }