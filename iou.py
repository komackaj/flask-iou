#!/usr/bin/python3

import sys
import traceback

import flask

from iou import config

app = flask.Flask(__name__)

@app.route('/')
def index():
    return "IOU OK"

@app.errorhandler(Exception)
def internal_server_error(error):
    traceback.print_exc()
    return "Internal server error", 500

if __name__ == '__main__':
    import argparse
    parse = argparse.ArgumentParser()
    parse.add_argument("--listen", default="0.0.0.0", help="Interface to listen on")
    parse.add_argument("--port", type=int, default=5000, help="Port to listen on")
    parse.add_argument("--debug", action="store_true", help="Enable debug mode")
    args = parse.parse_args()

    app.run(args.listen, port=args.port, debug=args.debug)
