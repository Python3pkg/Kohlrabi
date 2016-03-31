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
        pass
