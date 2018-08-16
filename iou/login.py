import flask
import flask_login
from flask_dance.contrib.google import make_google_blueprint, google
from flask_dance.consumer import oauth_authorized

import iou.config as config
from iou.models import User

google_blueprint = make_google_blueprint(
    scope=["email"],
    **config.googleAuth
)

login_manager = flask_login.LoginManager()
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
def google_logged_in(blueprint, token, testing=False):
    if not token:
        flask.flash("Failed to log in with {name}".format(name=blueprint.name))
        return

    if testing:
        email = token
    else:
        resp = blueprint.session.get('/oauth2/v2/userinfo')
        if not resp.ok:
            print("Invalid response", resp.status_code, resp.text)
            flask.abort(500)

        data = resp.json()
        email = data.get('email')
        if not email:
            print("Email not present in ", data)
            flask.abort(500)

    user = User.getOrCreate(email)
    flask_login.login_user(user)
