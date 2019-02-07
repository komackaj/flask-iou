import os
import traceback

import flask
from flask_login import login_required, current_user, logout_user
import sqlalchemy.orm.exc as saException
import werkzeug.exceptions as HTTPException

from iou.models import db, Offer, User
from iou.schemas import init_app_db, schemas

app = flask.Flask(__name__)
app.config.from_object("iou.config")
if 'FLASK_IOU_SETTINGS' in os.environ:
    app.config.from_envvar('FLASK_IOU_SETTINGS')
init_app_db(app)

def create_tables():
    with app.app_context():
        db.create_all()

@app.route('/fakeLogin')
def fakeLogin():
    from iou.login import google_logged_in
    email = flask.request.args['email']
    google_logged_in(None, email, testing=True)
    return "OK"

@app.route('/')
def index():
    return flask.render_template('index.html')

@app.route('/offers')
def offers():
    params = {
        'offers': Offer.query.all(),
        'users' : User.query.all(),
    }
    return flask.render_template('offers.html', **params)

@app.route('/people')
def people():
    return flask.render_template('people.html', users=User.query.all())

@app.route('/transactions')
def transactions():
    return flask.render_template('transactions.html')

@app.route('/edit-offer')
def edit_offer():
    return flask.render_template('offer-form.html')

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
    if flask.request.method == 'POST' and modelName == 'transaction':
        flask.abort(403)
    return schemas[modelName]

@app.route('/api/<modelName>/', methods=['GET'])
def schemaList(modelName):
    return schemaOrAbort(modelName).list()

@app.route('/api/<modelName>/', methods=['POST'])
def schemaCreate(modelName):
    inData = flask.request.json or flask.request.form.to_dict()
    data = schemaOrAbort(modelName).create(inData)
    return flask.make_response(data, 201)

@app.route('/api/<modelName>/<int:id>')
def schemaDetail(modelName, id):
    return schemaOrAbort(modelName).detail(id)

@app.route('/api/offer/<int:id>/accept', methods=['POST'])
def acceptOffer(id):
    amount = flask.request.json.get('amount')
    transaction = schemaOrAbort('offer').accept(id, amount)
    return schemas['transaction'].jsonify(transaction)

@app.route('/api/offer/<int:id>/decline', methods=['POST'])
def declineOffer(id):
    schemaOrAbort('offer').decline(id)
    return flask.make_response("No content", 204)

@app.errorhandler(Exception)
def internal_server_error(error):
    if isinstance(error, HTTPException.HTTPException):
        return error

    if isinstance(error, saException.NoResultFound):
        return HTTPException.NotFound()

    if isinstance(error, ValueError):
        return HTTPException.BadRequest()

    traceback.print_exc()
    return "Internal server error", 500
