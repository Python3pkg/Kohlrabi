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
    pass


a()


@kh.task
def b():
    pass


b()
