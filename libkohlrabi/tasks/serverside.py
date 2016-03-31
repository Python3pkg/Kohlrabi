"""
Server-side Task.
"""
import asyncio
import inspect

import sys

from .base import TaskBase

# Check if we're Python 3.5
PY35 = sys.version_info >= (3, 5, 0)


class TaskStub(object):
    """
    A object that masks the underlying coroutine on the server side.
    """

    def __init__(self, coro):
        self.coro = coro
        # __iter__ and __next__  are mapped to the coro __iter__ and __next__.
        self.__iter__ = self.coro.__iter__
        self.__next__ = self.coro.__next__
        # Map self.send and self.throw
        self.send = self.coro.send
        self.throw = self.coro.throw
        self.close = self.coro.close
        # Map __await__
        if PY35:
            if inspect.iscoroutine(coro):
                self.__await__ = self.coro.__await__


class ServerTaskBase(TaskBase):
    """
    Base class for a server-side task.
    """

    def invoke_func(self, *args, **kwargs):
        # Create a new Task stub.
        tstub = TaskStub(self.coro(*args, **kwargs))

