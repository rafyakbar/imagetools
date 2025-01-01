from celery import Celery
import os
import json
from PIL import Image
import pytesseract

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

            print(f"File JSON hasil kompresi disimpan di: {result_json_path}")
            return compressed_file_location
    except Exception as e:
        print(f"Terjadi kesalahan saat mengompres gambar: {e}")
        return None

@celery.task(name='upscale_image_task')
def upscale_image_task(file_location, scale_factor):
    """
    Mengubah ukuran gambar berdasarkan lokasi file dan faktor skala yang diberikan.

    :param file_location: Lokasi file gambar yang akan diubah ukurannya.
    :param scale_factor: Faktor skala untuk mengubah ukuran gambar.
    """
    try:
        # Membuka gambar
        with Image.open(file_location) as img:
            # Menghitung ukuran baru
            new_size = (int(img.width * scale_factor), int(img.height * scale_factor))

            # Mengubah ukuran gambar
            upscaled_image = img.resize(new_size, Image.LANCZOS)

            # Menyimpan gambar yang telah diubah ukurannya
            output_dir = "results/upscale_service"
            os.makedirs(output_dir, exist_ok=True)  # Membuat direktori jika belum ada

            basename = os.path.splitext(os.path.basename(file_location))[0]

            upscaled_file_location = os.path.join(
                output_dir,
                f"{basename}.jpg"
            )
            upscaled_image.save(upscaled_file_location, "JPEG")

            print(f"Gambar berhasil diubah ukurannya dan disimpan di: {upscaled_file_location}")

            # Membuat file JSON dengan hasil upscale
            result_json_path = os.path.join("success", f"{basename}.json")
            result_data = {
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

            print(f"File JSON hasil upscale disimpan di: {result_json_path}")
            return upscaled_file_location
    except Exception as e:
        print(f"Terjadi kesalahan saat mengubah ukuran gambar: {e}")
        return None

@celery.task(name='extract_text_task')
def extract_text_task(file_location):
    """
    Mengekstrak teks dari gambar berdasarkan lokasi file yang diberikan.

    :param file_location: Lokasi file gambar yang akan diekstrak teksnya.
    """
    try:
        # Membuka gambar
        with Image.open(file_location) as img:
            # Menggunakan pytesseract untuk mengekstrak teks
            extracted_text = pytesseract.image_to_string(img)

            basename = os.path.splitext(os.path.basename(file_location))[0]

            # Membuat file JSON dengan hasil ekstraksi
            result_json_path = os.path.join("success", f"{basename}.json")
            result_data = {
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