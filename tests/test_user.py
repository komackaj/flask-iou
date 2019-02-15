#!/usr/bin/python3

import unittest
from base import TestBase

class LoginTest(TestBase):

    def test_anonymous_login(self):
        info = self.call('/user')
        self.assertIsNone(info['user'])

    def test_logged_in(self):
        with self.client:
            email = 'a@test.com'
            self.login(email)
            info = self.call('/user')
            self.assertEqual(email, info['user']['email'])

    def test_new_user_has_zero_credit(self):
        with self.client:
            self.login('credit_zero@test.com')
            info = self.call('/user')
            self.assertEqual(0, info['user']['credit'])

    def test_user_cannot_change_his_credit(self):
        with self.client:
            user = self.login('self_credit_changer@test.com')
            self.assertEqual(0, user['credit'])

            userUrl = '/api/user/{}'.format(user['id'])
            self.call(userUrl, credit=20, expectedStatus=405)
            self.assertEqual(0, self.call('/user')['user']['credit'])

if __name__ == "__main__":
    unittest.main(verbosity=2)
