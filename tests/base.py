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

    def setUp(self):
        self.client = self.app.test_client()
        self.app.app_context().push()

    @classmethod
    def tearDownClass(cls):
        f = cls.app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', '')
        os.remove(f)

    def call(self, endpoint, expectedStatus=200, **kwargs):
        response = self.client.post(endpoint, json=kwargs) if kwargs else self.client.get(endpoint)
        self.assertEqual(expectedStatus, response.status_code)
        return json.loads(response.get_data(as_text=True)) if response.status_code < 300 else {}

    def createUser(self, email):
        userData = self.call('/api/user/', expectedStatus=201, email=email)
        return userData['id']

    def login(self, email):
        return self.call('/user', email=email)['user']

if __name__ == "__main__":
    unittest.main(verbosity=2)
