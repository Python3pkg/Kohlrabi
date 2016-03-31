"""
Kohlrabi object class.
"""
import asyncio
import types

from libkohlrabi.tasks import TaskBase, ServerTaskBase, ClientTaskBase
from libkohlrabi import VERSION_S
from libkohlrabi import kettage
from libkohlrabi import util
import os
import logging

logger = logging.getLogger("Kohlrabi")


class Kohlrabi(object):
    """
    A Kohlrabi task runner.
    """

    def __init__(self, kettage_ip: str, kettage_port: int, redis_ip: str = None, redis_port: int = None,
                 side: int = 0, redis_enabled: bool = False, thread_count: int = 2):
        """
        Create a new task runner.
        :param side: The side. 0 for client, 1 for server. Automatically set.
        :param kettage_ip: The IP for the Kettage server.
        :param kettage_port: The port for the Kettage server.
        :param redis_ip: The IP address for the Redis server. Optional.
        :param redis_port: The port for the Redis server.
        """
        self._loop = asyncio.get_event_loop()
        self._k_ip = kettage_ip
        self._k_port = kettage_port
        self._r_enabled = redis_enabled and ((redis_ip is not None) and (redis_port is not None))
        self._r_ip = redis_ip
        self._r_port = redis_port

        self.thread_count = thread_count

        self.tasks = {}

        # Change side.
        if os.environ.pop("KOHLRABI_SERVER", "0") == "1":
            # Force server-side
            self.side = 1
        else:
            self.side = side

        # Create a connection.
        if self.side == 1:
            self.kettage_connection_pull = self._get_kettage_conn(1)
        self.kettage_connection_push = self._get_kettage_conn(0)
        assert isinstance(self.kettage_connection_push, kettage.KettageConnection)
        assert isinstance(self.kettage_connection_pull, kettage.KettageConnection)

        if self.side == 1:
            self._logger_output()

    def _task_factory(self) -> TaskBase:
        """
        Create a new Task type.
        """
        if self.side == 0:
            return ClientTaskBase
        elif self.side == 1:
            return ServerTaskBase

    def task(self, func):
        """
        A decorator to create a task.

        :return: A TaskBase for the function, sided as appropriate.
        """
        # Generate an ID.
        f_id = func.__module__ + "." + func.__name__
        logger.debug("Registered task ID {}".format(f_id))
        # Create a new Task
        task_obb = self._task_factory()(func)
        self.tasks[f_id] = task_obb
        return task_obb

    def _logger_output(self):
        """
        Output logger data on server run
        """
        logger.info("Kohlrabi {} server-side object starting...".format(VERSION_S))

    def _get_kettage_conn(self, action, queue="kohlrabi-tasks"):
        # Create a Future.
        fut = asyncio.Future()
        asyncio.ensure_future(util.wraps_future(fut, kettage.create_connection(self._k_ip, self._k_port,
                                                                               queue, action)))
        self._loop.run_until_complete(fut)
        return fut.result()

    def begin(self):
        """
        Start the Kohlrabi server.
        """
        logger.info("Kohlrabi entering main.")
        try:
            self._loop.run_forever()
        except (KeyboardInterrupt, EOFError):
            self._loop.stop()
        finally:
            self._loop.close()
        logger.info("Kohlrabi exiting.")

    def apply_task(self, task: TaskBase):
        """
        Apply a task to be run.
        """
