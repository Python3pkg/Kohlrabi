"""
Server-side Task.
"""
import asyncio
import inspect

import sys

from .base import TaskBase

# Check if we're Python 3.5
PY35 = sys.version_info >= (3, 5, 0)


class ServerTaskBase(TaskBase):
    """
    Base class for a server-side task.
    """
    @asyncio.coroutine
    def invoke_func(self, ack_id, *args, **kwargs):
        # Yield from the coroutine.
        # This will run everything down the chain, hopefully.
        result = (yield from self.coro(*args, **kwargs))
        # Set the result in redis.
        yield from self.kohlrabi.send_msg("{}-RESULT".format(ack_id))
