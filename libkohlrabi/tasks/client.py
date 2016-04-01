"""
Client-side task.
"""
import asyncio

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
        return self.kohlrabi._loop.run_until_complete(self._redis_get_func_result())

    def result_with_timeout(self, timeout):
        return self.kohlrabi._loop.run_until_complete(self._redis_get_func_result(timeout=timeout))


class ClientTaskBase(TaskBase):
    """
    Base class for a client-side task.
    """

    def invoke_func(self, *args, **kwargs):
        # Tell the Kohlrabi instance to pack it up and send it to the server.
        ack_id = self.loop.run_until_complete(self.kohlrabi.apply_task(self, *args, **kwargs))
        return ClientTaskResult(ack_id, self.task_id, self.kohlrabi)
