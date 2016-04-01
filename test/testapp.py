"""
Test app for Kohlrabi
"""
from libkohlrabi import kohlrabi
import logging

logging.basicConfig(level=logging.INFO)

# --> Init Kohlrabi
kh = kohlrabi.Kohlrabi()


@kh.task
def b(passed_s: str):
    print("This is much more natural than Celery syntax.")


@kh.task
def a(arg1):
    print(arg1)
    yield from b("test")


@kh.task
def add(a, b):
    return a + b


if __name__ == "__main__":
    a("hello, world")
    added = add(1, 2).result_with_timeout(0)
    print(added)
