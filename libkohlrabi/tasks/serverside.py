"""
Server-side Task.
"""
import asyncio
import sys
import traceback
import logging

import aioredis
import msgpack

from .base import TaskBase


logger = logging.getLogger("Kohlrabi")

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
        try:
            result = (yield from self.coro(*args, **kwargs))  # Yield with the arguments passed in.
        except Exception as e:
            logger.debug("Caught error: {}".format(e))
            with (yield from self.kohlrabi.redis_conn) as redis:
                assert isinstance(redis, aioredis.Redis)
                # Format the exception data.
                tb = traceback.format_exc()
                # Pack the exception data.
                exc_data = msgpack.packb({"exc": e.__class__.__name__, "msg": ' '.join(e.args)})
                redis.set("{}-EXC".format(ack_id), exc_data)
                redis.set("{}-TB".format(ack_id), tb)
                result = ""
        # Set the result in redis.
        yield from self.kohlrabi.send_msg(result, queue="{}-RESULT".format(ack_id))
