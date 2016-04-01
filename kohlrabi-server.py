#!/usr/bin/env python3
"""
Kohlrabi is an asyncio-based task queue server.

It requires a connection to a Kettage server and a Redis server (for results).
"""
import argparse

from libkohlrabi import server
import os

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("app_object", help="App object to load Kohlrabi from - in format package.file:obj")
    args = parser.parse_args()
    os.environ["KOHLRABI_SERVER"] = "1"
    server.run(args)
