#!/usr/bin/python3
# -*- coding: utf-8 -*-

import argparse
import sys

from iou.app import app, create_tables

if __name__ == '__main__':
    parse = argparse.ArgumentParser()
    parse.add_argument("--listen", default="0.0.0.0", help="Interface to listen on")
    parse.add_argument("--port", type=int, default=5000, help="Port to listen on")
    parse.add_argument("--debug", action="store_true", help="Enable debug mode")
    parse.add_argument("--create-tables", action="store_true", help="Create tables in DB")
    args = parse.parse_args()

    if args.create_tables:
        create_tables()
        sys.exit(0)

    app.run(args.listen, port=args.port, debug=args.debug)
