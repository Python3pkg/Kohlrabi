"""
Utilities.
"""
import asyncio

SIDE_CLIENT = 0
SIDE_SERVER = 1

@asyncio.coroutine
def wraps_future(fut: asyncio.Future, coro):
    # Yield from coroutine.
    result = yield from coro
    fut.set_result(result)
