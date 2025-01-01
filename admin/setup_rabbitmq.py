import pika
import time
import os

# Konfigurasi RabbitMQ
RABBITMQ_HOST = os.getenv('RABBITMQ_HOST', 'rabbitmq')
RABBITMQ_USER = os.getenv('RABBITMQ_USER', 'guest')
RABBITMQ_PASS = os.getenv('RABBITMQ_PASS', 'guest')

def setup_rabbitmq():
    # Membuat koneksi ke RabbitMQ
    credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASS)
    parameters = pika.ConnectionParameters(host=RABBITMQ_HOST, credentials=credentials)
    connection = pika.BlockingConnection(parameters=parameters)
    channel = connection.channel()

    # Exchange
    exchange_name = 'imagetools.image_processing'
    channel.exchange_declare(exchange=exchange_name, exchange_type='topic')

    # Queues dan Routing Keys
    queue_routing_keys = {
        'imagetools.compress_image_queue': 'imagetools.compress',
        'imagetools.upscale_image_queue': 'imagetools.upscale',
        'imagetools.extract_text_queue': 'imagetools.extract'
    }

    # Bind Queue ke Exchange
    for queue, routing_key in queue_routing_keys.items():
        channel.queue_declare(queue=queue, durable=True)
        channel.queue_bind(
            exchange=exchange_name,
            queue=queue,
            routing_key=routing_key
        )

    print("Exchange, Queue, dan Binding telah diatur.")

    # Menutup koneksi
    connection.close()

if __name__ == '__main__':
    # Tunggu beberapa detik agar RabbitMQ siap
    time.sleep(30)
    setup_rabbitmq()
