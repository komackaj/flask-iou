#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
import traceback

import flask

from iou import config
from iou.models import init_app_db, user_schema

app = flask.Flask(__name__)
init_app_db(app, config)

@app.route('/')
def index():
    return "IOU OK"

@app.route('/users/', methods=['GET', 'POST'])
def users():
    if flask.request.method == 'POST':
        new_obj = user_schema.make_instance(flask.request.json)
        db.session.add(new_obj)
        db.session.commit()
        return flask.make_response(user_schema.jsonify(new_obj), 201)
    else:
        all_objs = user_schema.Meta.model.query.all()
        return user_schema.jsonify(all_objs, many=True)

@app.route('/users/<id>')
def user_detail(id):
    obj = user_schema.Meta.model.query.get(id)
    return user_schema.jsonify(obj)

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
