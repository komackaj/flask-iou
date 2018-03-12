# -*- coding: utf-8 -*-

from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow

db = SQLAlchemy()
ma = Marshmallow()

def init_app_db(app, config):
    app.config['SQLALCHEMY_DATABASE_URI'] = config.db_connection_string
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = config.sqlalchemy_track_modifications
    db.init_app(app)
    ma.init_app(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)

    def __repr__(self):
        return '<User %r>' % self.name

class UserSchema(ma.ModelSchema):
    class Meta:
        model = User

user_schema = UserSchema()
