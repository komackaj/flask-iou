import flask
from flask_login import LoginManager, login_user
from flask_dance.contrib.google import make_google_blueprint, google
from flask_dance.consumer import oauth_authorized

import iou.config as config
from iou.models import db, User

google_blueprint = make_google_blueprint(
    scope=["email"],
    **config.googleAuth
)

login_manager = LoginManager()
login_manager.login_view = 'google.login'

def init_app(app, danceAlchemyBackend):
    app.secret_key = config.secret_key
    login_manager.init_app(app)
    google_blueprint.backend = danceAlchemyBackend
    app.register_blueprint(google_blueprint, url_prefix="/login")

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@oauth_authorized.connect_via(google_blueprint)
def google_logged_in(blueprint, token):
    if not token:
        flask.flash("Failed to log in with {name}".format(name=blueprint.name))
        return

    resp = blueprint.session.get('/oauth2/v2/userinfo')
    if not resp.ok:
        print("Invalid response", resp.status_code, resp.text)
        flask.abort(500)

    data = resp.json()
    email = data.get('email')
    if not email:
        print("Email not present in ", data)
        flask.abort(500)

    user = User.query.filter_by(email=email).first()
    if user is None:
        user = User(email=email)
        db.session.add(user)
        db.session.commit()

    login_user(user)
