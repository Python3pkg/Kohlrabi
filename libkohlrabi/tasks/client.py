"""
Client-side task.
"""
import asyncio
from .base import TaskBase


class ClientTaskBase(TaskBase):
    """
    Base class for a client-side task.
    """

    def invoke_func(self, *args, **kwargs):
        # Tell the Kohlrabi instance to pack it up and send it to the server.
        self.loop.run_until_complete(self.kohlrabi.apply_task(self, *args, **kwargs))
