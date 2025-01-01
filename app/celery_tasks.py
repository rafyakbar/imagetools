from celery import Celery
import os

RABBITMQ_HOST = os.getenv('RABBITMQ_HOST', 'rabbitmq')
RABBITMQ_USER = os.getenv('RABBITMQ_USER', 'guest')
RABBITMQ_PASS = os.getenv('RABBITMQ_PASS', 'guest')

celery = Celery(
    'imagetools',
    broker=f'amqp://{RABBITMQ_USER}:{RABBITMQ_PASS}@{RABBITMQ_HOST}//',
    backend='rpc://'
)

@celery.task(name='add_task')
def add_task(x, y):
   result = x + y
   print(result)
   return result