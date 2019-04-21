# -*- coding: utf-8 -*-

import iou.models as models
import iou.social_login as social_login

from flask_marshmallow import Marshmallow
from flask_login import current_user, login_user
import werkzeug.exceptions as HTTPException

ma = Marshmallow()

def init_app_db(app):
    models.db.init_app(app)
    social_login.init_app(app, models.danceAlchemyBackend)
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

    def _create_obj(self, data):
        new_obj = self.make_instance(data)
        models.db.session.add(new_obj)
        models.db.session.commit()
        return new_obj

    def create(self, data):
        new_obj = self._create_obj(data)
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
        dump_only = ['credit']

    def _getOrCreate(self, data, method):
        username = data['username']
        password = data['password']
        if username and password:
            user = method(username, password)
            if user:
                login_user(user)
        return self.current()

    def create(self, data):
        return self._getOrCreate(data, self.Meta.model.create)

    def login(self, data):
        return self._getOrCreate(data, self.Meta.model.get)

    def current(self):
        user = current_user if current_user.is_authenticated else None
        return self.jsonify(user)

class OAuthSchema(SchemaBase):
    class Meta:
        model = models.OAuth

class OfferSchema(SchemaBase):
    class Meta:
        model = models.Offer

    class Permission:
        accept = decline = 'target'
        remove = 'owner'

    def accept(self, id, amount=None):
        offer = self.Meta.model.query.get(id)
        if offer.target:
            self.validate(offer, 'accept')
        return offer.accept(amount=amount)

    def create(self, inData):
        targetId = inData.get('targetId')
        if current_user.id == 1 and targetId is not None:
            offer = self._create_obj(inData)
            target = models.User.query.get(targetId)
            transaction = offer.accept(target=target)
            return schemas['transaction'].jsonify(transaction)
        else:
            return super().create(inData)

    def _checkAndRemove(self, id, action):
        offer = self.Meta.model.query.get(id)
        self.validate(offer, action)
        models.db.session.delete(offer)
        models.db.session.commit()

    def decline(self, id):
        self._checkAndRemove(id, 'decline')

    def remove(self, id):
        self._checkAndRemove(id, 'remove')

class TransactionSchema(SchemaBase):
    class Meta:
        model = models.Transaction

# example entry: 'user': UserSchema()
schemas = {
    schema.Meta.model.__name__.lower(): schema()
    for schema in SchemaBase.__subclasses__()
}
