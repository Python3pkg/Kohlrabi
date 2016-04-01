"""
Base task class.
"""
import asyncio
import types


class TaskBase(object):
    """
    Base task.
    """

    def __init__(self, kh, func: types.FunctionType, id=None):
        self._func = func
        self.coro = self._wrap_func(func)
        self.loop = asyncio.get_event_loop()

        self.kohlrabi = kh

        self.task_id = id if id else self._func.__module__ + "." + self._func.__name__

    def __call__(self, *args, **kwargs):
        return self.invoke_func(*args, **kwargs)

    @staticmethod
    def _wrap_func(func_obj: types.FunctionType) -> types.FunctionType:
        # Wrap function to produce a coroutine
        # async def or generator function flag
        if (func_obj.__code__.co_flags & 0x180) or (func_obj.__code__.co_flags & 0x20):
            return func_obj
        else:
            return asyncio.coroutine(func_obj)

    def invoke_func(self, *args, **kwargs):
        """
        Invoke the function.

        This is different on server side and client side.
        """
        raise NotImplementedError
