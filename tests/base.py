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
        cls.adminEmail = 'admin@test.com'
        cls.adminId = None

    def setUp(self):
        cls = self.__class__
        self.client = self.app.test_client()
        self.app.app_context().push()
        if cls.adminId is None:
            cls.adminId = self.createUser(self.adminEmail)['id']

    @classmethod
    def tearDownClass(cls):
        f = cls.app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', '')
        os.remove(f)

    def call(self, endpoint, expectedStatus=200, **kwargs):
        response = self.client.post(endpoint, json=kwargs) if kwargs else self.client.get(endpoint)
        if isinstance(expectedStatus, (tuple, list)):
            self.assertIn(response.status_code, expectedStatus)
        else:
            self.assertEqual(expectedStatus, response.status_code)
        hasData = response.status_code < 300 and response.status_code != 204
        return json.loads(response.get_data(as_text=True)) if hasData else {}

    def createUser(self, username, password='pass'):
        return self.call('/api/user/', expectedStatus=201, username=username, password=password)

    def login(self, username, password='pass'):
        return self.call('/api/user/login', username=username, password=password, expectedStatus=(200, 201))

    def loginAsAdmin(self):
        return self.login(self.adminEmail)

if __name__ == "__main__":
    unittest.main(verbosity=2)
