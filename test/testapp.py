"""
Test app for Kohlrabi
"""
from libkohlrabi import kohlrabi
import logging

logging.basicConfig(level=logging.DEBUG)

# --> Init Kohlrabi
kh = kohlrabi.Kohlrabi()


@kh.task
def b(passed_s: str):
    print("This is much more natural than Celery syntax.")


@kh.task
def a(arg1):
    print(arg1)
    yield from b("test")


if __name__ == "__main__":
    a("hello, world")
