"""
A simple utility that sends Packet's to a Redis List.
"""
import queue
import sys
import threading

import redis

from wishpy.wireshark.lib.dissector import (
        WishpyDissectorQueuePython,
        setup_process,
        cleanup_process)

from wishpy.libpcap.lib.capturer import LibpcapCapturer

_REDIS_DB = 7

class RedisPacketPublisherError(Exception):
    pass

class RedisPacketPublisher:

    def __init__(self, redis_client, capturer, dissector):

        self.__redis_client = redis_client
        self.__capturer = capturer
        self.__dissector = dissector

        self.__initialized = False
        self.__capturer_started = False
        self.__stop_requested = False

        self.__capturer_thread = None

    def init(self):
        """Initialize all the moving parts.
        """
        self.__capturer.open()

        setup_process()

        self.__initialized = True

    def start(self):

        self.__capturer_thread = threading.Thread(
                target=self.__capturer.start, args=()).start()
        self.__capturer_started = True
        print("Capturer started.")
        self.run()

    def run(self):
        """Run through our `start` method.
        """
        if not self.__initialized:
            raise RedisPacketPublisherError("Packet Capture is not initialized.")
        if not self.__capturer_started:
            raise RedisPacketPublisherError("Packet Capture is not started.")

        for _, _, d in self.__dissector.run():
            print(d)
            self.__redis_client.rpush('paket_queue:wlp2s0', d)


        # Comes here after dissector is stopped. Join the capturer thread
        self.__capturer_thread.join()
        return

    def stop(self):
        """Stop's the machinery.
        """
        self.__stop_requested = True
        self.__capturer.stop()
        self.__dissector.stop()

    def __del__(self):
        cleanup_process()

def _main(args):

    _ = args #Ignoring for now

    redis_client = redis.Redis(db=_REDIS_DB)

    _internal_q = queue.Queue()

    capturer = LibpcapCapturer("wlp2s0", _internal_q)

    dissector = WishpyDissectorQueuePython(_internal_q)

    publisher = RedisPacketPublisher(redis_client, capturer, dissector)
    publisher.init()
    try:

        publisher.start()

    except KeyboardInterrupt:
        publisher.stop()


if __name__ == '__main__':

    _main(sys.argv)

