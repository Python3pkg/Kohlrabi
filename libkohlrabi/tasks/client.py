"""
Client-side task.
"""
import sys

from redis.client import Redis
import msgpack

from .base import TaskBase


class ClientTaskResult(object):
    """
    An object that represents the result of a ClientTask.

    Used to get the result of the coro.
    """

    def __init__(self, ack_id, task_id, kh, redis):
        self.ack_id = ack_id
        self.task_id = task_id
        self.kohlrabi = kh
        self.redis = redis

    def _redis_get_func_result(self, timeout=30):
        assert isinstance(self.redis, Redis)
        result = self.redis.blpop("{}-RESULT".format(self.ack_id), timeout=timeout)[1]
        exc = self._redis_get_exc()
        if exc:
            unpacked = msgpack.unpackb(exc, encoding='utf-8')
            # get the traceback
            tb = self.redis.get("{}-TB".format(self.ack_id))
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
        return self._redis_get_func_result(60 ** 5)

    def result_with_timeout(self, timeout):
        return self._redis_get_func_result(timeout=timeout)

    def _redis_get_func_finished(self):
        return self.redis.exists("{}-RESULT".format(self.ack_id))

    def _redis_get_exc(self):
        exc = self.redis.get("{}-EXC".format(self.ack_id))
        return exc

    @property
    def finished(self):
        return self._redis_get_func_finished()


class ClientTaskBase(TaskBase):
    """
    Base class for a client-side task.
    """

    def invoke_func(self, *args, **kwargs):
        # Tell the Kohlrabi instance to pack it up and send it to the server.

        ack_id = self.loop.run_until_complete(self.kohlrabi.apply_task(self, *args, **kwargs))
        return ClientTaskResult(ack_id, self.task_id, self.kohlrabi, self.kohlrabi._blocking_redis)
