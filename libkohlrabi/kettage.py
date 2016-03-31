"""
Kettage connection utils.
"""
import msgpack
import asyncio
import logging

loop = asyncio.get_event_loop()

logger = logging.getLogger("Kohlrabi")


class KettageConnection(object):
    def __init__(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        self.reader = reader
        self.writer = writer

    @asyncio.coroutine
    def get_msg(self):
        msgpack.pack({"action": 1}, self.writer)
        result = yield from self.reader.read(n=65536)
        return msgpack.unpackb(result)

    @asyncio.coroutine
    def send_msg(self, data):
        msgpack.pack({"action": 0, "data": data}, self.writer)
        result = yield from self.reader.read(n=65536)
        return msgpack.unpackb(result)


@asyncio.coroutine
def create_connection(ip: str, port: int, queue: str, action: int):
    try:
        reader, writer = yield from asyncio.open_connection(host=ip, port=port)
    except ConnectionRefusedError:
        logger.error("Connection to Kettage refused - is server running?")
        return None
    msgpack.pack({"queue": queue, "action": action}, writer)
    return KettageConnection(reader, writer)
