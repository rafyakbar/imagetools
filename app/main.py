from fastapi import FastAPI, UploadFile, File, Form
import os
import uuid
import json
from celery_tasks import add_task

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

    # Mengembalikan nama file dan path lengkap sistem
    return file_name, os.path.abspath(full_path)

@app.get("/")
def index():
    return {"status": "ok"}

@app.get("/run")
def handle_run():
   task_response = add_task.delay(5, 6)
   print(task_response)
   return {"message": "Task execution started"}