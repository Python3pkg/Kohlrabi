"""
Client-side task.
"""
import asyncio

import aioredis

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
