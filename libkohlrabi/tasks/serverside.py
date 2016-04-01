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
    def invoke_func(self, *args, **kwargs):
        # Send off to our helper function that handles setting values.
        pass
