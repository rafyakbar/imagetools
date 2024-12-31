import pika
import time

# Konfigurasi RabbitMQ
RABBITMQ_HOST = 'rabbitmq'
RABBITMQ_USER = 'guest'
RABBITMQ_PASS = 'guest'

# Fungsi untuk mengatur Exchange, Queue, dan Binding
def setup_rabbitmq():
    # Membuat koneksi ke RabbitMQ
    credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASS)
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST, credentials=credentials))
    channel = connection.channel()

    # Mendefinisikan Exchange
    exchange_name = 'image_tools_exchange'
    channel.exchange_declare(exchange=exchange_name, exchange_type='direct')

    # Mendefinisikan Queue
    queue_name = 'image_tasks_queue'
    channel.queue_declare(queue=queue_name)

    # Mengikat Queue ke Exchange
    routing_key = 'image_task'
    channel.queue_bind(exchange=exchange_name, queue=queue_name, routing_key=routing_key)

    print("Exchange, Queue, dan Binding telah diatur.")

    # Menutup koneksi
    connection.close()

if __name__ == '__main__':
    # Tunggu RabbitMQ siap
    time.sleep(30)  # Tunggu beberapa detik agar RabbitMQ siap
    setup_rabbitmq()