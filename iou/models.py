# -*- coding: utf-8 -*-

from datetime import datetime

from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, current_user
from flask_dance.consumer.backend.sqla import OAuthConsumerMixin, SQLAlchemyBackend
from flask_dance.consumer import oauth_authorized

db = SQLAlchemy()

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=True)
    password = db.Column(db.String)
    email = db.Column(db.String(80), unique=True)
    credit = db.Column(db.Integer, default=0)

    def __repr__(self):
        return '<User %r>' % self.email

    @classmethod
    def create(cls, username, password, email=None):
        user = cls.query.filter_by(username=username).first()
        if user is not None:
            return ValueError("User exists already")

        user = cls(username=username, password=password, email=email)
        db.session.add(user)
        db.session.commit()
        return user

    @classmethod
    def get(cls, username, password):
        user = cls.query.filter_by(username=username).first()
        if user is None or not cls._verify_password(user, password):
            return None
        return user

    @classmethod
    def getOrCreate(cls, username, password):
        user = cls.query.filter_by(username=username).first()
        if not user:
            return cls.create(username, password, email=None)

        if not cls._verify_password(user, password):
            raise ValueError()
        return user

    @classmethod
    def getByEmail(cls, email):
        user = cls.query.filter_by(email=email).first()
        return user

    @staticmethod
    def _verify_password(user, password):
        return user.password == password

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

    def accept(self, target=current_user, amount=None):
        # convert offer to transaction
        # specify amount for partial accept

        if amount is not None:
            if amount <= 0:
                raise ValueError("Invalid amount - must be at least 1")
            if amount > self.amount:
                raise ValueError("Invalid amount - can accept up to {}".format(offer.amount))

        transaction = Transaction.fromOffer(self)
        if transaction.targetId is None:
            transaction.target = target
        if amount and amount < self.amount:
            self.amount -= amount
            transaction.amount = amount
        else:
            db.session.delete(self)

        owner = User.query.get(self.ownerId)
        value = transaction.amount * transaction.price
        owner.credit += value
        target.credit -= value

        db.session.add(owner)
        db.session.add(transaction)
        db.session.commit()
        return transaction

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
