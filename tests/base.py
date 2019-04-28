#!/usr/bin/python3

import json
import os
import unittest

class TestBase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        os.environ['FLASK_IOU_SETTINGS'] = '../tests/config.cfg'
        from iou.app import app, create_tables
        cls.app = app
        cls.app.testing = True
        create_tables()
        cls.adminEmail = 'testadmin@test.com'
        cls.adminId = None

    def setUp(self):
        cls = self.__class__
        self.client = self.app.test_client()
        self.app.app_context().push()
        if cls.adminId is None:
            cls.adminId = self.createUser(self.adminEmail)

    @classmethod
    def tearDownClass(cls):
        f = cls.app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', '')
        os.remove(f)

    def call(self, endpoint, expectedStatus=200, **kwargs):
        response = self.client.post(endpoint, json=kwargs) if kwargs else self.client.get(endpoint)
        self.assertEqual(expectedStatus, response.status_code)
        hasData = response.status_code < 300 and response.status_code != 204
        return json.loads(response.get_data(as_text=True)) if hasData else {}

    def createUser(self, email):
        userData = self.call('/api/user/', expectedStatus=201, email=email)
        return userData['id']

    def login(self, email):
        return self.call('/user', email=email)['user']

if __name__ == "__main__":
    unittest.main(verbosity=2)
