import os
import time

import pika
from flask import current_app

RABBIT_HOST = os.environ.get("RABBIT_HOST")
RABBIT_PORT = os.environ.get("RABBIT_PORT")


class RabbitConnectionPool:
    def __init__(self):
        pass

    def init(self, app):
        with app.app_context():
            self.connection = None
            self.desired_channels = 5
            self.channels = []
            self.free_channels = []
            self._reset_channels()
            current_app.logger.info("Connected to RabbitMQ and created queues.")

    def _reset_channels(self):
        if self.connection is None:
            try:
                self.connection = pika.BlockingConnection(
                    pika.ConnectionParameters(host=RABBIT_HOST, port=RABBIT_PORT)
                )
            except pika.exceptions.AMQPConnectionError:
                current_app.logger.warn(
                    "Failed to connect to RabbitMQ service. Message wont be sent."
                )
                return
            for i in range(self.desired_channels):
                channel = self.connection.channel()
                channel.queue_declare(queue="receipt_queue", durable=True)
                channel.queue_declare(queue="report_queue", durable=True)
                self.channels.append(channel)
                self.free_channels.append(channel)
            current_app.logger.info("Connection and channels reset.")

    def publish_message(self, routing_key, body, properties):
        if self.connection is None:
            self._reset_channels()

            attempts_count = 0
            while self.connection is None:
                time.sleep(3)
                self._reset_channels()
                attempts_count += 1
                if attempts_count == 10:
                    raise Exception("Can't connect to RabbitMQ")

        while len(self.free_channels) == 0:
            time.sleep(3)
        try:
            channel = self.free_channels.pop()
            channel.basic_publish(
                exchange="", routing_key=routing_key, body=body, properties=properties
            )
            current_app.logger.info("Message published")
            self.free_channels.append(channel)
        except pika.exceptions.StreamLostError:
            current_app.logger.warn("Stream lost. Creating new connection.")
            self.connection = None
            self._reset_channels()

            attempts_count = 0
            while self.connection is None:
                time.sleep(3)
                self._reset_channels()
                attempts_count += 1
                if attempts_count == 10:
                    raise Exception("Can't connect to RabbitMQ")
            channel = self.free_channels.pop()
            channel.basic_publish(
                exchange="", routing_key=routing_key, body=body, properties=properties
            )
            current_app.logger.info("Message published")
            self.free_channels.append(channel)


def init_queues():
    try:
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(host=RABBIT_HOST, port=RABBIT_PORT)
        )
    except pika.exceptions.AMQPConnectionError:
        return
    channel = connection.channel()
    channel.queue_declare(queue="receipt_queue", durable=True)
    channel.queue_declare(queue="report_queue", durable=True)
    connection.close()

POOL = RabbitConnectionPool()