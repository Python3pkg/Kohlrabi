"""
Test app for Kohlrabi
"""
from libkohlrabi import kohlrabi
import logging

logging.basicConfig(level=logging.INFO)

# --> Init Kohlrabi
kh = kohlrabi.Kohlrabi()


@kh.task
def a(arg1):
    # Print the argument passed to it.
    print(arg1)
    yield from b("test")


@kh.task
def b(passed_s: str):
    print("This is much more natural than Celery syntax.")
    print("String that was passed:", passed_s)


@kh.task
def add(a, b):
    c


if __name__ == "__main__":
    # Call a() with hello world.
    # This is transmitted to the server.
    qq = a("hello, world")
    print(qq.finished)
    added = add(1, 2).result_with_timeout(1)
    print(added)
