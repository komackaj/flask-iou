# -*- coding: utf-8 -*-
import iou.models as models
from flask_marshmallow import Marshmallow

ma = Marshmallow()

def init_app_db(app, config):
    models.db.init_app(app)
    ma.init_app(app)

class SchemaBase(ma.ModelSchema):

    def create(self, data):
        new_obj = self.make_instance(data)
        models.db.session.add(new_obj)
        models.db.session.commit()
        return self.jsonify(new_obj)

    def detail(self, id):
        obj = self.Meta.model.query.get(id)
        return self.jsonify(obj)

    def list(self):
        all_objs = self.Meta.model.query.all()
        return self.jsonify(all_objs, many=True)

class UserSchema(SchemaBase):
    class Meta:
        model = models.User

# example entry: 'user': UserSchema()
schemas = {
    schema.Meta.model.__name__.lower(): schema()
    for schema in SchemaBase.__subclasses__()
}
