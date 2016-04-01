"""
Client-side task.
"""
import asyncio
import sys

import aioredis
import msgpack

from .base import TaskBase


class ClientTaskResult(object):
    """
    An object that represents the result of a ClientTask.

    Used to get the result of the coro.
    """

    def __init__(self, ack_id: int, task_id: str, kh):
        self.ack_id = ack_id
        self.task_id = task_id
        self.kohlrabi = kh

    @asyncio.coroutine
    def _redis_get_func_result(self, timeout=30):
        result = yield from asyncio.wait_for(
            self.kohlrabi.get_msg(queue="{}-RESULT".format(self.ack_id)), timeout=timeout
        )
        exc = yield from self._redis_get_exc()
        if exc:
            unpacked = msgpack.unpackb(exc, encoding='utf-8')
            # get the traceback
            with (yield from self.kohlrabi.redis_conn) as redis:
                assert isinstance(redis, aioredis.Redis)
                tb = yield from redis.get("{}-TB".format(self.ack_id))
                if tb: tb = tb.decode()
                print(tb, file=sys.stderr)
                print("The above exception was the direct cause of the following exception:\n", file=sys.stderr)
            # try and load the attribute
            raise __builtins__[unpacked["exc"]](unpacked["msg"])
        return result

    @property
    def result(self):
        # Retrieve the result from redis.
        # Stupidly long timeout, a little under twenty-five years.
        return self.kohlrabi._loop.run_until_complete(self._redis_get_func_result(60**5))

    def result_with_timeout(self, timeout):
        return self.kohlrabi._loop.run_until_complete(self._redis_get_func_result(timeout=timeout))

    @asyncio.coroutine
    def _redis_get_func_finished(self):
        with (yield from self.kohlrabi.redis_conn) as redis:
            assert isinstance(redis, aioredis.Redis)
            return redis.exists("{}-RESULT".format(self.ack_id))

    @asyncio.coroutine
    def _redis_get_exc(self):
        with (yield from self.kohlrabi.redis_conn) as redis:
            assert isinstance(redis, aioredis.Redis)
            exc = yield from redis.get("{}-EXC".format(self.ack_id))
            return exc

    @property
    def finished(self):
        return self.kohlrabi._loop.run_until_complete(self._redis_get_func_finished())


class ClientTaskBase(TaskBase):
    """
    Base class for a client-side task.
    """

    def invoke_func(self, *args, **kwargs):
        # Tell the Kohlrabi instance to pack it up and send it to the server.
        ack_id = self.loop.run_until_complete(self.kohlrabi.apply_task(self, *args, **kwargs))
        return ClientTaskResult(ack_id, self.task_id, self.kohlrabi)
