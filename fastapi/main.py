from fastapi import FastAPI, UploadFile, File, Form
import pika
import os
import uuid
import json
import time

app = FastAPI()

# Konfigurasi RabbitMQ
RABBITMQ_HOST = os.getenv('RABBITMQ_HOST', 'rabbitmq')  # Mengambil dari variabel lingkungan
RABBITMQ_USER = os.getenv('RABBITMQ_USER', 'guest')
RABBITMQ_PASS = os.getenv('RABBITMQ_PASS', 'guest')

# Membuat direktori uploaded jika belum ada
UPLOAD_DIR = "uploaded"
os.makedirs(UPLOAD_DIR, exist_ok=True)

def publish_message(routing_key, message):
    credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASS)
    for attempt in range(5):  # Coba 5 kali
        try:
            connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST, credentials=credentials))
            channel = connection.channel()

            exchange_name = 'imagetools.image_processing'
            channel.basic_publish(exchange=exchange_name, routing_key=routing_key,
                                  body=json.dumps(message))  # Mengirim pesan dalam format JSON

            connection.close()
            return  # Jika berhasil, keluar dari fungsi
        except Exception as e:
            print(f"Attempt {attempt + 1}: Error publishing message: {e}")
            time.sleep(2)  # Tunggu 2 detik sebelum mencoba lagi
    raise Exception("Failed to connect to RabbitMQ after several attempts.")


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
    return file_name, os.path.abspath(full_path)  # Mengembalikan file_name dan full_path

@app.post("/upload/")
async def upload_file(file: UploadFile = File(...)):
    upload_folder = "uploaded"  # Folder di dalam container
    file_location = os.path.join(UPLOAD_DIR + '/extract_service', file.filename)

    with open(file_location, "wb") as f:
        f.write(await file.read())

    return {"info": f"File '{file.filename}' saved at '{file_location}'"}

@app.post("/compress/")
async def compress_image(
        file: UploadFile = File(...),
        compression_rate: int = Form(...)):  # Menambahkan parameter untuk tingkat kompresi
    # Membuat direktori untuk compress_service jika belum ada
    compress_dir = os.path.join(UPLOAD_DIR, "compress_service")
    os.makedirs(compress_dir, exist_ok=True)

    # Simpan file di dalam folder compress_service
    file_location = await save_file(compress_dir, file)

    # Kirim pesan ke RabbitMQ dengan tingkat kompresi
    message = {
        "file_location": file_location,
        "compression_rate": compression_rate
    }
    publish_message('imagetools.compress', message)

    return {"message": "Image compression started", "file_location": file_location,
            "compression_rate": compression_rate}

@app.post("/upscale/")
async def upscale_image(
        file: UploadFile = File(...),
        upscale_rate: int = Form(...)):  # Menambahkan parameter untuk tingkat upscale
    # Membuat direktori untuk upscale_service jika belum ada
    upscale_dir = os.path.join(UPLOAD_DIR, "upscale_service")
    os.makedirs(upscale_dir, exist_ok=True)

    # Simpan file di dalam folder upscale_service
    file_location = await save_file(upscale_dir, file)

    # Kirim pesan ke RabbitMQ dengan tingkat upscale
    message = {
        "file_location": file_location,
        "upscale_rate": upscale_rate
    }
    publish_message('imagetools.upscale', message)

    return {"message": "Image upscaling started", "file_location": file_location, "upscale_rate": upscale_rate}

@app.post("/extract/")
async def extract_text(file: UploadFile = File(...)):
    # Membuat direktori untuk extract_service jika belum ada
    extract_dir = os.path.join(UPLOAD_DIR, "extract_service")
    os.makedirs(extract_dir, exist_ok=True)

    # Simpan file di dalam folder extract_service
    file_location = await save_file(extract_dir, file)

    # Kirim pesan ke RabbitMQ
    message = {
        "file_location": file_location
    }
    # publish_message('imagetools.extract', message)

    return {"message": "Text extraction started", "file_location": file_location}

@app.get("/")
def index():
    return {"status": "ok"}