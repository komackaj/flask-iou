#!/usr/bin/python3

import json
import os
import unittest

class LoginTest(unittest.TestCase):

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

    def call(self, endpoint, **kwargs):
        response = self.client.post(endpoint, json=kwargs) if kwargs else self.client.get(endpoint)
        self.assertEqual(200, response.status_code)
        return json.loads(response.get_data(as_text=True))

    def login(self, email):
        return self.call('/user', email=email)

    def test_anonymous(self):
        info = self.call('/user')
        self.assertIsNone(info['user'])

    def test_logged_in(self):
        with self.client:
            email = 'a@test.com'
            self.login(email)
            info = self.call('/user')
            user = info['user']
            self.assertEqual(email, user['email'])

if __name__ == "__main__":
    unittest.main(verbosity=2)
