"""
Test app for Kohlrabi
"""
from libkohlrabi import kohlrabi
import logging

logging.basicConfig(level=logging.DEBUG)

# --> Init Kohlrabi
kh = kohlrabi.Kohlrabi(kettage_ip="127.0.0.1", kettage_port=3423, redis_enabled=True)


@kh.task
def a():
    pass

a()