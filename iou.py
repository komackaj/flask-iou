#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
import traceback

import flask
from flask_login import login_required, current_user, logout_user

from iou.schemas import init_app_db, schemas

app = flask.Flask(__name__)
app.config.from_object("iou.config")
init_app_db(app)

@app.route('/')
def index():
    return "IOU OK"

@app.route('/login')
@login_required
def login():
    return "Logged in as " + current_user.email

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return flask.redirect(flask.url_for('index'))


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
