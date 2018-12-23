#!/usr/bin/python3

import unittest
from base import TestBase

class LoginTest(TestBase):
    def test_anonymous(self):
        info = self.call('/user')
        self.assertIsNone(info['user'])

    def test_logged_in(self):
        with self.client:
            email = 'a@test.com'
            self.login(email)
            info = self.call('/user')
            self.assertEqual(email, info['user']['email'])

if __name__ == "__main__":
    unittest.main(verbosity=2)
