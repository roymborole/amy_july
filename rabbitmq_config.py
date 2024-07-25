import pika
import os

def get_rabbitmq_connection():
    rabbitmq_host = os.environ.get('RABBITMQ_HOST')
    rabbitmq_port = int(os.environ.get('RABBITMQ_PORT', 5672))
    rabbitmq_user = os.environ.get('RABBITMQ_USER')
    rabbitmq_pass = os.environ.get('RABBITMQ_PASS')
    rabbitmq_vhost = os.environ.get('RABBITMQ_VHOST', '/')

    credentials = pika.PlainCredentials(rabbitmq_user, rabbitmq_pass)
    parameters = pika.ConnectionParameters(
        host=rabbitmq_host,
        port=rabbitmq_port,
        virtual_host=rabbitmq_vhost,
        credentials=credentials
    )
    return pika.BlockingConnection(parameters)

def get_channel(connection):
    return connection.channel()