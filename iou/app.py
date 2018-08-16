import os
import traceback

import flask
from flask_login import login_required, current_user, logout_user

from iou.models import db
from iou.schemas import init_app_db, schemas

app = flask.Flask(__name__)
app.config.from_object("iou.config")
if 'FLASK_IOU_SETTINGS' in os.environ:
    app.config.from_envvar('FLASK_IOU_SETTINGS')
init_app_db(app)

def create_tables():
    with app.app_context():
        db.create_all()

@app.route('/')
def index():
    return "IOU OK"

@app.route('/user', methods=["GET", "POST"])
def user():
    if app.testing and flask.request.method == "POST":
        from iou.login import google_logged_in
        email = flask.request.json['email']
        google_logged_in(None, email, app.testing)

    user = schemas['user'].dump(current_user)[0] if current_user.is_authenticated else None
    return flask.jsonify(user=user)

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
