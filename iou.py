#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
import traceback

import flask

from iou import config, login
from iou.schemas import init_app_db, schemas

app = flask.Flask(__name__)
init_app_db(app, config)
login.init_app(app)

@app.route('/')
@login.logged
def index():
    return "IOU OK"

def schemaOrAbort(modelName):
    if modelName not in schemas:
        flask.abort(404)
    return schemas[modelName]

@app.route('/api/<modelName>/', methods=['GET'])
def schemaList(modelName):
    return schemaOrAbort(modelName).list()

@app.route('/api/<modelName>/', methods=['POST'])
def schemaCreate(modelName):
    data = schemaOrAbort(modelName).create(flask.request.json)
    return flask.make_response(data, 201)

@app.route('/api/<modelName>/<int:id>')
def schemaDetail(modelName, id):
    return schemaOrAbort(modelName).detail(id)

@app.errorhandler(Exception)
def internal_server_error(error):
    traceback.print_exc()
    return "Internal server error", 500

if __name__ == '__main__':
    import argparse
    import sys
    from iou.models import db

    parse = argparse.ArgumentParser()
    parse.add_argument("--listen", default="0.0.0.0", help="Interface to listen on")
    parse.add_argument("--port", type=int, default=5000, help="Port to listen on")
    parse.add_argument("--debug", action="store_true", help="Enable debug mode")
    parse.add_argument("--create-tables", action="store_true", help="Create tables in DB")
    args = parse.parse_args()

    if args.create_tables:
        with app.app_context():
            db.create_all()
            sys.exit(0)

    app.run(args.listen, port=args.port, debug=args.debug)
