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

from wishpy.libpcap.lib.capturer import WishpyCapturerIfaceToQueue

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

    def start(self, redis_queue):

        self.__capturer_thread = threading.Thread(
                target=self.__capturer.start, args=())
        try:
            self.__capturer_thread.start()
            self.__capturer_started = True
            print("Capturer started.")
            self.run(redis_queue)
        except Exception as e:
            print(e)
            raise

    def run(self, redis_queue):
        """Run through our `start` method.
        """
        if not self.__initialized:
            raise RedisPacketPublisherError("Packet Capture is not initialized.")
        if not self.__capturer_started:
            raise RedisPacketPublisherError("Packet Capture is not started.")

        try:
            for _, _, d in self.__dissector.run():
                print(d)
                self.__redis_client.rpush(redis_queue, d)
        except KeyboardInterrupt:
            print("Stop Requested, stopping Capturer.")
        except Exception as e:
            print(e)

        finally:
            # Should never come here other than - Exceptions or Keyboard Interrupt
            self.stop()


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

    if len(args) != 2:
        print("Usage: wishpy_redis.py <interface-name>")
        sys.exit(1)

    iface_name = args[1]
    redis_queue = "packet_queue:{}".format(iface_name)

    redis_client = redis.Redis(db=_REDIS_DB)

    _internal_q = queue.Queue()

    capturer = WishpyCapturerIfaceToQueue(iface_name, _internal_q)

    dissector = WishpyDissectorQueuePython(_internal_q)

    publisher = RedisPacketPublisher(redis_client, capturer, dissector)
    try:

        publisher.init()

        publisher.start(redis_queue)

    except KeyboardInterrupt:
        publisher.stop()
    except Exception as e:
        print(e)
        sys.exit(1)
        publisher.stop()



if __name__ == '__main__':

    _main(sys.argv)

