from celery import Celery
import os
import json
from PIL import Image
import pytesseract
from kombu import Exchange, Queue
import time

RABBITMQ_HOST = os.getenv('RABBITMQ_HOST', 'rabbitmq')
RABBITMQ_USER = os.getenv('RABBITMQ_USER', 'guest')
RABBITMQ_PASS = os.getenv('RABBITMQ_PASS', 'guest')

celery = Celery(
    'imagetools',
    broker=f'amqp://{RABBITMQ_USER}:{RABBITMQ_PASS}@{RABBITMQ_HOST}//',
    backend='rpc://'
)

# CUSTOM BINDING (ROUTE)
# referensi https://docs.celeryq.dev/en/latest/userguide/routing.html

# Queues dengan routing keys
queue_routing_keys = {
    'imagetools.compress_image_queue': 'imagetools.compress',
    'imagetools.upscale_image_queue': 'imagetools.upscale',
    'imagetools.extract_text_queue': 'imagetools.extract'
}

# Definisikan exchange
exchange_name = 'imagetools.image_processing'
image_processing_exchange = Exchange(exchange_name, type='topic')

# Buat custom queues
celery.conf.task_queues = (
    Queue(
        name='imagetools.compress_image_queue',
        exchange=image_processing_exchange,
        routing_key=queue_routing_keys['imagetools.compress_image_queue']
    ),
    Queue(
        name='imagetools.upscale_image_queue',
        exchange=image_processing_exchange,
        routing_key=queue_routing_keys['imagetools.upscale_image_queue']
    ),
    Queue(
        name='imagetools.extract_text_queue',
        exchange=image_processing_exchange,
        routing_key=queue_routing_keys['imagetools.extract_text_queue']
    ),
)

# Konfigurasi routing
celery.conf.task_routes = {
    'compress_image_task': {'queue': 'imagetools.compress_image_queue'},
    'upscale_image_task': {'queue': 'imagetools.upscale_image_queue'},
    'extract_text_task': {'queue': 'imagetools.extract_text_queue'},
}

@celery.task(name='compress_image_task')
def compress_image_task(file_location, compression_rate):
    """
    Mengompres gambar berdasarkan lokasi file dan tingkat kompresi yang diberikan.

    :param file_location: Lokasi file gambar yang akan dikompres.
    :param compression_rate: Tingkat kompresi (0-100), di mana 100 adalah kualitas tertinggi.
    """
    try:
        start_time = time.time()  # Waktu mulai eksekusi

        # Membuka gambar
        with Image.open(file_location) as img:
            # Menghitung kualitas kompresi dan memastikan nilai antara 1 dan 100
            quality = max(1, min(100, compression_rate))

            # Menyimpan gambar yang telah dikompres & membuat folder jika belum ada
            output_dir = "results/compress_service"
            os.makedirs(output_dir, exist_ok=True)

            basename = os.path.splitext(os.path.basename(file_location))[0]

            # Simpan gambar hasil kompresi
            compressed_file_location = os.path.join(
                output_dir,
                f"{basename}.jpg"
            )
            img.save(compressed_file_location, "JPEG", quality=quality)

            print(f"Gambar berhasil dikompres dan disimpan di: {compressed_file_location}")

            # Membuat data file JSON
            result_json_path = os.path.join("success", f"{basename}.json")
            execution_time = time.time() - start_time
            result_data = {
                "execution_time": f"{execution_time:.6f} detik",
                "service": "compress",
                "parameters": {
                    'file_location': file_location,
                    'compression_rate': compression_rate,
                    'computed_compression_rate': quality
                },
                "result": {
                    "type": "image",
                    "input": file_location,
                    "output": compressed_file_location,
                }
            }

            with open(result_json_path, "w") as json_file:
                json.dump(result_data, json_file)

            print(f"File JSON disimpan di: {result_json_path}")
            return compressed_file_location
    except Exception as e:
        print(f"Terjadi kesalahan saat mengompres gambar: {e}")
        return None

@celery.task(name='upscale_image_task')
def upscale_image_task(file_location, scale_factor):
    """
    Mengubah ukuran gambar berdasarkan lokasi file dan skala yang diberikan.

    :param file_location: Lokasi file gambar yang akan diubah ukurannya.
    :param scale_factor: Skala untuk mengubah ukuran gambar.
    """
    try:
        start_time = time.time()  # Waktu mulai eksekusi

        # Membuka gambar
        with Image.open(file_location) as img:
            # Menghitung ukuran baru
            new_size = (int(img.width * scale_factor), int(img.height * scale_factor))

            # Mengubah ukuran gambar
            upscaled_image = img.resize(new_size, Image.LANCZOS)

            # Menyimpan gambar yang telah diubah ukurannya & membuat direktori jika belum ada
            output_dir = "results/upscale_service"
            os.makedirs(output_dir, exist_ok=True)

            basename = os.path.splitext(os.path.basename(file_location))[0]

            # Simpan hasil upscale gambar
            upscaled_file_location = os.path.join(
                output_dir,
                f"{basename}.jpg"
            )
            upscaled_image.save(upscaled_file_location, "JPEG")

            print(f"Gambar berhasil diubah ukurannya dan disimpan di: {upscaled_file_location}")

            # Membuat file JSON
            result_json_path = os.path.join("success", f"{basename}.json")
            execution_time = time.time() - start_time
            result_data = {
                "execution_time": f"{execution_time:.6f} detik",
                "service": "upscale",
                "parameters": {
                    'file_location': file_location,
                    'scale_factor': scale_factor
                },
                "result": {
                    "type": "image",
                    "input": file_location,
                    "output": upscaled_file_location,
                }
            }

            with open(result_json_path, "w") as json_file:
                json.dump(result_data, json_file)

            print(f"File JSON disimpan di: {result_json_path}")
            return upscaled_file_location
    except Exception as e:
        print(f"Terjadi kesalahan saat mengubah ukuran gambar: {e}")
        return None

@celery.task(name='extract_text_task', queue='imagetools.extract_text_queue')
def extract_text_task(file_location):
    """
    Mengekstrak teks dari gambar berdasarkan lokasi file yang diberikan.

    :param file_location: Lokasi file gambar yang akan diekstrak teksnya.
    """
    try:
        start_time = time.time()  # Waktu mulai eksekusi

        # Membuka gambar
        with Image.open(file_location) as img:
            # Menggunakan pytesseract untuk mengekstrak teks
            extracted_text = pytesseract.image_to_string(img)

            basename = os.path.splitext(os.path.basename(file_location))[0]

            # Membuat file JSON dengan hasil ekstraksi
            result_json_path = os.path.join("success", f"{basename}.json")
            execution_time = time.time() - start_time
            result_data = {
                "execution_time": f"{execution_time:.6f} detik",
                "service": "extract_text",
                "parameters": {
                    'file_location': file_location
                },
                "result": {
                    "type": "text",
                    "input": file_location,
                    "output": extracted_text
                }
            }

            with open(result_json_path, "w") as json_file:
                json.dump(result_data, json_file)

            print(f"File JSON hasil ekstraksi disimpan di: {result_json_path}")
            return extracted_text
    except Exception as e:
        print(f"Terjadi kesalahan saat mengekstrak teks: {e}")
        return None