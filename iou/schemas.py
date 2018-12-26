# -*- coding: utf-8 -*-

import iou.models as models
import iou.login as login

from flask_marshmallow import Marshmallow
from flask_login import current_user
import werkzeug.exceptions as HTTPException

ma = Marshmallow()


def init_app_db(app):
    models.db.init_app(app)
    login.init_app(app, models.danceAlchemyBackend)
    ma.init_app(app)

class SchemaBase(ma.ModelSchema):

    def validate(self, obj, action):
        ownerFields = getattr(self.Permission or {}, action, None)
        if not ownerFields:
            return

        if isinstance(ownerFields, str):
            ownerFields = [ownerFields]

        owners = [getattr(obj, field) for field in ownerFields]
        if all(current_user!=owner for owner in owners):
            raise HTTPException.Forbidden()

    def create(self, data):
        new_obj = self.make_instance(data)
        models.db.session.add(new_obj)
        models.db.session.commit()
        return self.jsonify(new_obj)

    def detail(self, id):
        obj = self.Meta.model.query.filter_by(id=id).one()
        return self.jsonify(obj)

    def list(self):
        all_objs = self.Meta.model.query.all()
        return self.jsonify(all_objs, many=True)

class UserSchema(SchemaBase):
    class Meta:
        model = models.User

class OAuthSchema(SchemaBase):
    class Meta:
        model = models.OAuth

class OfferSchema(SchemaBase):
    class Meta:
        model = models.Offer

    class Permission:
        accept = deny = 'target'

    def accept(self, id, amount=None):
        # convert offer to transaction
        # specify amount for partial accept

        offer = self.Meta.model.query.get(id)
        if offer.target:
            self.validate(offer, 'accept')

        if amount is not None:
            if amount <= 0:
                raise ValueError("Invalid amount - must be at least 1")
            if amount > offer.amount:
                raise ValueError("Invalid amount - can accept up to {}".format(offer.amount))

        transaction = models.Transaction.fromOffer(offer)
        if amount and amount < offer.amount:
            offer.amount -= amount
            transaction.amount = amount
        else:
            models.db.session.delete(offer)

        models.db.session.add(transaction)
        models.db.session.commit()
        return transaction

    def deny(self, id):
        offer = self.Meta.model.query.get(id)
        self.validate(offer, 'deny')
        models.db.session.delete(offer)
        models.db.session.commit()

class TransactionSchema(SchemaBase):
    class Meta:
        model = models.Transaction

# example entry: 'user': UserSchema()
schemas = {
    schema.Meta.model.__name__.lower(): schema()
    for schema in SchemaBase.__subclasses__()
}
