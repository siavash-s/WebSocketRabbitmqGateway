from logging import getLogger
from queue import Queue
from threading import Thread
from typing import Callable
import os
import logging


class RabbitReader(Thread):

    def __init__(self, input_queue: Queue, receiver_callback: Callable):
        """

        :param input_queue: the queue in which the reader will read from
        :param receiver_callback: the callback that accept a key(str) and a payload(str) on message receive
            the callback may raise KeyError if provided key does not exists or not allowed
        """
        super().__init__()
        self.input_queue = input_queue
        self.receiver_callback = receiver_callback
        self.daemon = True

    def __read(self):
        key, message = self.input_queue.get(block=True)
        try:
            self.receiver_callback(key, message)
        except KeyError as e:
            getLogger().error(
                "rabbit reader callback error, key not allowed or does not exists, key: '{}', message: '{}'".format(
                    key, message
                )
            )

    def run(self):
        while True:
            try:
                self.__read()
            except Exception as e:
                getLogger().info("rabbit reader thread caught unhandled exception")
                logging.exception(e)
                os._exit(1)
