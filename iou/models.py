# -*- coding: utf-8 -*-

from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, current_user
from flask_dance.consumer.backend.sqla import OAuthConsumerMixin, SQLAlchemyBackend
from flask_dance.consumer import oauth_authorized

db = SQLAlchemy()

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(80), unique=True, nullable=False)

    def __repr__(self):
        return '<User %r>' % self.email

    @classmethod
    def getOrCreate(cls, email):
        user = cls.query.filter_by(email=email).first()
        if user is None:
            user = cls(email=email)
            db.session.add(user)
            db.session.commit()
        return user

class OAuth(db.Model, OAuthConsumerMixin):
    __tablename__ = "flask_dance_oauth"

    user_id = db.Column(db.Integer, db.ForeignKey(User.id))
    user = db.relationship(User)

# TODO: use cache as per https://flask-dance.readthedocs.io/en/latest/backends.html#sqlalchemy
danceAlchemyBackend = SQLAlchemyBackend(OAuth, db.session, user=current_user)
