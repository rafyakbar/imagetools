from celery import Celery
import os
import json
from PIL import Image

RABBITMQ_HOST = os.getenv('RABBITMQ_HOST', 'rabbitmq')
RABBITMQ_USER = os.getenv('RABBITMQ_USER', 'guest')
RABBITMQ_PASS = os.getenv('RABBITMQ_PASS', 'guest')

celery = Celery(
    'imagetools',
    broker=f'amqp://{RABBITMQ_USER}:{RABBITMQ_PASS}@{RABBITMQ_HOST}//',
    backend='rpc://'
)


@celery.task(name='compress_image_task')
def compress_image_task(file_location, compression_rate):
    """
    Mengompres gambar berdasarkan lokasi file dan tingkat kompresi yang diberikan.

    :param file_location: Lokasi file gambar yang akan dikompres.
    :param compression_rate: Tingkat kompresi (0-100), di mana 100 adalah kualitas tertinggi.
    """
    try:
        # Membuka gambar
        with Image.open(file_location) as img:
            # Menghitung kualitas kompresi dan memastikan nilai antara 1 dan 100
            quality = max(1, min(100, compression_rate))

            # Menyimpan gambar yang telah dikompres
            output_dir = "results/compress_service"
            os.makedirs(output_dir, exist_ok=True)  # Membuat direktori jika belum ada

            basename = os.path.splitext(os.path.basename(file_location))[0]

            compressed_file_location = os.path.join(
                output_dir,
                f"{basename}.jpg"
            )
            img.save(compressed_file_location, "JPEG", quality=quality)

            print(f"Gambar berhasil dikompres dan disimpan di: {compressed_file_location}")

            # Membuat file JSON dengan hasil kompresi
            result_json_path = os.path.join("success", f"{basename}.json")
            result_data = {
                "service": "compress",
                "parameters": {
                    'file_location': file_location,
                    'compression_rate': compression_rate
                },
                "result": {
                    "quality": quality,
                    "before": file_location,
                    "after": compressed_file_location,
                }
            }

            with open(result_json_path, "w") as json_file:
                json.dump(result_data, json_file)

            print(f"File JSON hasil kompresi disimpan di: {result_json_path}")
            return compressed_file_location
    except Exception as e:
        print(f"Terjadi kesalahan saat mengompres gambar: {e}")
        return None