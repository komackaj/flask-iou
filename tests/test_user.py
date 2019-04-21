#!/usr/bin/python3

import unittest
from base import TestBase

class LoginTest(TestBase):

    def test_anonymous_login(self):
        self.call('/logout', expectedStatus=302)
        info = self.call('/api/user/current')
        self.assertEqual(info, {})

    def test_logged_in(self):
        with self.client:
            info = self.createUser(username='regtest', password='abracadabra')
            self.assertEqual('regtest', info['username'])

    def test_new_user_has_zero_credit(self):
        with self.client:
            user = self.createUser('credit_zero@test.com')
            self.assertEqual(0, user['credit'])

    def test_user_cannot_change_his_credit(self):
        with self.client:
            user = self.createUser('self_credit_changer@test.com')
            self.assertEqual(0, user['credit'])

            userUrl = '/api/user/{}'.format(user['id'])
            self.call(userUrl, credit=20, expectedStatus=405)
            user = self.call('/api/user/current')
            self.assertEqual(0, user['credit'])

if __name__ == "__main__":
    unittest.main(verbosity=2)
