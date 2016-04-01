"""
Kohlrabi object class.
"""
import asyncio
import logging
import os
import random

import aioredis
import msgpack

from libkohlrabi import VERSION_S
from libkohlrabi.tasks import TaskBase, ServerTaskBase, ClientTaskBase

logger = logging.getLogger("Kohlrabi")


class Kohlrabi(object):
    """
    A Kohlrabi task runner.
    """

    def __init__(self, redis_ip: str = "127.0.0.1", redis_port: int = 6379,
                 side: int = 0, thread_count: int = 2):
        """
        Create a new task runner.
        :param side: The side. 0 for client, 1 for server. Automatically set.
        :param redis_ip: The IP address for the Redis server.
        :param redis_port: The port for the Redis server.
        """
        self._loop = asyncio.get_event_loop()
        self._r_ip = redis_ip
        self._r_port = redis_port

        # Create a redis connection
        self.redis_conn = self._loop.run_until_complete(aioredis.create_pool((self._r_ip, self._r_port)))

        self.thread_count = thread_count

        self.tasks = {}

        # Change side.
        if os.environ.pop("KOHLRABI_SERVER", "0") == "1":
            # Force server-side
            self.side = 1
        else:
            self.side = side

        if self.side == 1:
            self._logger_output()
        else:
            logger.debug("Kohlrabi client object loaded and connected")

    def __del__(self):
        # Stop the horrible asyncio logging spammery
        self._loop.set_exception_handler(lambda *args, **kwargs: True)

    def _task_factory(self) -> TaskBase:
        """
        Create a new Task type.
        """
        if self.side == 0:
            return ClientTaskBase
        elif self.side == 1:
            return ServerTaskBase

    def task(self, func):
        """
        A decorator to create a task.

        :return: A TaskBase for the function, sided as appropriate.
        """
        # Generate an ID.
        f_id = func.__module__ + "." + func.__name__
        if func.__module__ == "__main__":
            f_id = func.__code__.co_filename.split('/')[-1].split('.')[0] + '.' + func.__name__
            print("!! KOHLRABI - You should not define tasks in __main__! They cannot be mapped appropriately!")
            logger.critical("You should not define tasks in __main__! They cannot be mapped appropriately!")
            print("!! Taking best guess at function ID: {}".format(f_id))
            logger.critical("!! Taking best guess at function ID: {}".format(f_id))
        logger.debug("Registered task ID {}".format(f_id))
        # Create a new Task
        task_obb = self._task_factory()(self, func, id=f_id)
        self.tasks[f_id] = task_obb
        return task_obb

    def _logger_output(self):
        """
        Output logger data on server run
        """
        logger.info("Kohlrabi {} server-side object starting...".format(VERSION_S))

    @asyncio.coroutine
    def _server_register_on_redis(self):
        with (yield from self.redis_conn) as redis:
            assert isinstance(redis, aioredis.Redis)
            redis.incr("kohlrabi-workers")

    @asyncio.coroutine
    def _server_deregister_on_redis(self):
        with (yield from self.redis_conn) as redis:
            assert isinstance(redis, aioredis.Redis)
            redis.decr("kohlrabi-workers")

    @asyncio.coroutine
    def _get_num_servers_registered(self):
        with (yield from self.redis_conn) as redis:
            assert isinstance(redis, aioredis.Redis)
            return int((yield from redis.get("kohlrabi-workers")))

    def begin(self):
        """
        Start the Kohlrabi server.
        """
        logger.info("Kohlrabi entering main.")

        self._loop.create_task(self.serverside_task_loop())

        self._loop.run_until_complete(self._server_register_on_redis())

        logger.info("Kohlrabi registered as worker {}.".format(
            self._loop.run_until_complete(self._get_num_servers_registered())
        ))

        try:
            self._loop.run_forever()
        except (KeyboardInterrupt, EOFError):
            self._loop.stop()
        finally:
            self._loop.run_until_complete(self._server_deregister_on_redis())
            self._loop.close()
        logger.info("Kohlrabi exiting.")

    @asyncio.coroutine
    def serverside_task_loop(self):
        """
        The server side task loop. Fetches new tasks and executes them, as appropriate.
        """
        while True:
            try:
                msg_data = yield from self.get_msg()
            except RuntimeError as e:
                if e.args[0] == "Event loop is closed":
                    return
                else:
                    raise
            logger.debug("Got new task: {}".format(msg_data))
            # On the server side, try and get the function.
            func_id = msg_data['id']
            if func_id not in self.tasks:
                logger.critical("Could not find task `{}` on the server-side! Try reloading Kohlrabi.".format(func_id))
                continue
            task = self.tasks[func_id]
            # ACK that we got the func.
            with (yield from self.redis_conn) as redis:
                redis.lpush("{}-ACK".format(msg_data["ack"]), 1)
            # Run it on the server-side.
            assert isinstance(task, ServerTaskBase), "Task invocation should be happening on the server side"
            self._loop.create_task(task.invoke_func(msg_data["ack"], *msg_data["args"], **msg_data["kwargs"]))

    @asyncio.coroutine
    def apply_task(self, task: ClientTaskBase, *args, **kwargs):
        """
        Apply a task to be run.

        This is the main work house of Kohlrabi. It sends functions to run to the server side.

        :param task: The ClientTaskBase to apply to the server side.
        :param args: The args for the function to use
        :param kwargs: The kwargs for the function to use
        """
        # First, generate a random ACK ID.
        ack_id = random.randint(10 ** 9, 10 ** 10)
        # Package up the dictionary to send.
        to_send = {"id": task.task_id, "ack": ack_id, "args": args, "kwargs": kwargs}
        logger.debug("Packing up {} to send to the Kohlrabi server.".format(to_send))
        yield from self.send_msg(to_send)
        # Wait for the server to acknowledge the task
        acked = yield from self._wait_for_ack(ack_id)
        assert acked is True, "ack is NOT true - this should never happen!"
        return ack_id

    @asyncio.coroutine
    def _wait_for_ack(self, ack_id: int) -> bool:
        # Blocking pop {ack_id}-ACK.
        with (yield from self.redis_conn) as redis:
            data = (yield from redis.blpop("{}-ACK".format(ack_id)))[1]
            data = int(data)
            if data == 1:
                return True
            else:
                return False

    @asyncio.coroutine
    def get_msg(self, queue="kohlrabi-tasks"):
        """
        Get a new message off of the redis queue.

        This will automatically msgpack-decode the data, so don't use if you want to get raw values.

        :param queue: The queue to pick a message from.
        """
        with (yield from self.redis_conn) as redis:
            assert isinstance(redis, aioredis.Redis)
            data = (yield from redis.blpop(queue))[1]
            return msgpack.unpackb(data, encoding='utf-8')

    @asyncio.coroutine
    def send_msg(self, to_send, queue="kohlrabi-tasks"):
        """
        Put a message onto the queue.

        This will automatically msgpack-encode the data, including a 'use_bin_type' value so the resulting data can
        be decoded in UTF-8 properly.

        :param to_send: The data to send.
        :param queue: The queue to send the data to.
        """
        data = msgpack.packb(to_send, use_bin_type=True)
        with (yield from self.redis_conn) as redis:
            assert isinstance(redis, aioredis.Redis)
            yield from redis.lpush(queue, data)
