"""
Utilities.
"""
import sys

PY33 = sys.version_info[0:2] >= (3, 3)

SIDE_CLIENT = 0
SIDE_SERVER = 1

if PY33:
    import asyncio

    @asyncio.coroutine
    def wraps_future(fut: asyncio.Future, coro):
        # Yield from coroutine.
        result = yield from coro
        fut.set_result(result)


def SideOnly(side):
    def _side_wrapper(func):
        if func.__self__.side == side:
            return func
        else:
            def __err(*args, **kwargs):
                raise NameError("name '{}' is not defined".format(func.__name__))
            return __err
    return _side_wrapper