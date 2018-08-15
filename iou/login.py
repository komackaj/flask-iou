from functools import wraps

import flask
from flask_dance.contrib.google import make_google_blueprint, google

import iou.config as config

def init_app(app):
    app.secret_key = config.secret_key
    blueprint = make_google_blueprint(
        scope=["email"],
        **config.googleAuth
    )
    app.register_blueprint(blueprint, url_prefix="/login")

def logged(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not google.authorized:
            return flask.redirect(flask.url_for("google.login"))

        resp = google.get("/oauth2/v2/userinfo")
        email = resp.json()['email']
        print("OAuth email", email)

        return f(*args, **kwargs)
    return wrapper
