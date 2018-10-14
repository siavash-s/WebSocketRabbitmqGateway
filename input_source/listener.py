import logging
from logging import getLogger
from queue import Queue
from threading import Thread
from typing import Callable
import os
import pika
from pika.exceptions import AMQPConnectionError
import configs
from time import sleep


class RabbitListener(Thread):

    def __init__(
            self, exchange_name: str,
            exchange_type: str,
            topic: str,
            result_queue: Queue,
            queue_key: str,
            data_hook: Callable
    ):
        """

        :param queue: the listener will push results from the topic into the queue with (queue_key, result) format
        :param data_hook: callable that accepts one argument and outputs after transforming it
        """
        super().__init__()
        self.daemon = True
        self.exchange_name = exchange_name
        self.exchange_type = exchange_type
        self.topic = topic
        self.queue_key = queue_key
        self.result_queue = result_queue
        self.data_hook = data_hook

    def __listen(self):
        connection = pika.BlockingConnection(pika.ConnectionParameters(**configs.rabbitmq_connection))
        channel = connection.channel()
        channel.exchange_declare(
            exchange=self.exchange_name,
            exchange_type=self.exchange_type
        )

        result = channel.queue_declare(exclusive=True)
        queue_name = result.method.queue

        channel.queue_bind(
            exchange=self.exchange_name,
            queue=queue_name,
            routing_key=self.topic
        )

        def callback(ch, method, properties, body):
            try:
                body = body.decode("utf8")
            except UnicodeDecodeError as e:
                getLogger().info(
                    "error while decoding message from rabbitmq, using empty body, exchange: '{}', topic: '{}', "
                    "error: '{}'".format(
                        self.exchange_name, self.topic, repr(e)
                    )
                )
                body = ""
            self.result_queue.put((self.queue_key, self.data_hook(body)))

        channel.basic_consume(callback, queue=queue_name, no_ack=True)
        channel.start_consuming()

    def run(self):
        while True:
            try:
                self.__listen()
            except AMQPConnectionError as e:
                getLogger().error(
                    "rabbit connection error, retrying connection after {} secs".format(
                        configs.rabbitmq_connection_sleep_retry
                    )
                )
                logging.exception(e)
                sleep(configs.rabbitmq_connection_sleep_retry)
            except Exception as e:
                getLogger().info("exiting... ,rabbit listener thread encounter uncaught exception")
                logging.exception(e)
                os._exit(1)
