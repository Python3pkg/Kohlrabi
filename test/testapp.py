"""
Test app for Kohlrabi
"""
from libkohlrabi import kohlrabi
import logging

logging.basicConfig(level=logging.DEBUG)

# --> Init Kohlrabi
kh = kohlrabi.Kohlrabi()


@kh.task
def a():
    print("Hello, world!")


if __name__ == "__main__":
    a()

