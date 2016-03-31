"""
Utilities.
"""
import os
import sys
import asyncio


@asyncio.coroutine
def wraps_future(fut: asyncio.Future, coro):
    # Yield from coroutine.
    result = yield from coro
    fut.set_result(result)
