# -*- coding: utf-8 -*-

from datetime import datetime

from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, current_user
from flask_dance.consumer.backend.sqla import OAuthConsumerMixin, SQLAlchemyBackend
from flask_dance.consumer import oauth_authorized

db = SQLAlchemy()

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(80), unique=True, nullable=False)
    credit = db.Column(db.Integer, default=0)

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

class Offer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    item = db.Column(db.String)
    amount = db.Column(db.Integer)
    price = db.Column(db.Integer)
    ownerId = db.Column(db.Integer, db.ForeignKey(User.id), nullable=False)
    owner = db.relationship(User, foreign_keys=(ownerId,))
    targetId = db.Column(db.Integer, db.ForeignKey(User.id))
    target = db.relationship(User, foreign_keys=(targetId,))

    def __repr__(self):
        return '<Offer {0.id} by {0.ownerId}: {0.amount} {0.item} for {0.price} per pcs>'.format(self)

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    item = db.Column(db.String)
    amount = db.Column(db.Integer)
    price = db.Column(db.Integer)
    timestamp = db.Column(db.DateTime)
    ownerId = db.Column(db.Integer, db.ForeignKey(User.id), nullable=False)
    owner = db.relationship(User, foreign_keys=(ownerId,))
    targetId = db.Column(db.Integer, db.ForeignKey(User.id))
    target = db.relationship(User, foreign_keys=(targetId,))

    def __repr__(self):
        return '<Transaction {0.id} by {0.ownerId}: {0.amount} {0.item} for {0.price} per pcs, {0.timestamp}>'.format(self)

    @classmethod
    def fromOffer(cls, offer):
        result = cls()
        for key in ('item', 'amount', 'price', 'ownerId', 'targetId'):
            val = getattr(offer, key)
            setattr(result, key, val)
        result.timestamp = datetime.now()
        return result

# TODO: use cache as per https://flask-dance.readthedocs.io/en/latest/backends.html#sqlalchemy
danceAlchemyBackend = SQLAlchemyBackend(OAuth, db.session, user=current_user)
