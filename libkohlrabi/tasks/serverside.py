"""
Server-side Task.
"""
import asyncio
import sys

from .base import TaskBase

# Check if we're Python 3.5
PY35 = sys.version_info >= (3, 5, 0)


class ServerTaskBase(TaskBase):
    """
    Base class for a server-side task.
    """

    def __call__(self, *args, **kwargs):
        # On the server side, simply wrap around the coroutine's call.
        # This ensures that if you run a task on the server side, from another task normally, it will be invoked
        # normally.
        return self.coro(*args, **kwargs)

    @asyncio.coroutine
    def invoke_func(self, ack_id, *args, **kwargs):
        # Yield from the coroutine.
        # This will run everything down the chain, hopefully.
        result = (yield from self.coro(*args, **kwargs))  # Yield with the arguments passed in.
        # Set the result in redis.
        yield from self.kohlrabi.send_msg(result, queue="{}-RESULT".format(ack_id))
