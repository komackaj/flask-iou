#!/usr/bin/python3

import unittest
from base import TestBase

# TODO: tests for invalid amount
# TODO: tests for model edit permission

class OfferTest(TestBase):

    def createOffer(self, ownerId, item, amount, price, targetId=None):
        params = {
                "ownerId" : ownerId,
                "item"    : item,
                "amount"  : amount,
                "price"   : price,
                'targetId': targetId
            }
        return self.call("/api/offer/", expectedStatus=201, **params)

    def check_credit(self, expected):
        loggedUser = self.call('/user')['user']
        self.assertEqual(expected, loggedUser['credit'])

    def test_create_offer_without_target(self):
        def check(loginId, offer):
            self.assertGreater(offer['id'], -1)
            self.assertEqual(offer['item'], 'stone')
            self.assertEqual(offer['amount'], 1)
            self.assertEqual(offer['price'], 15)
            self.assertEqual(offer['owner'], loginId)
            self.assertIsNone(offer['target'])

        with self.client:
            email = 'a@test.com'
            loginId = self.login(email)['id']
            offer = self.createOffer(loginId, 'stone', amount=1, price=15)
            check(loginId, offer)
            offer = self.call("/api/offer/{}".format(offer['id']))
            check(loginId, offer)

    def test_create_accept_offer(self):
        with self.client:
            ownerEmail = 'a@test.com'
            targetEmail = 'b@test.com'

            # create offer as a
            ownerId = self.login(ownerEmail)['id']
            targetId = self.createUser(targetEmail)
            self.assertNotEqual(ownerId, targetId)
            offer = self.createOffer(ownerId, 'yoghurt', amount=3, price=10, targetId=targetId)
            self.assertGreater(offer['id'], -1)
            self.assertEqual(offer['owner'], ownerId)
            self.assertEqual(offer['target'], targetId)

            # login as b
            loginId = self.login(targetEmail)['id']
            self.assertEqual(targetId, loginId)
            loggedUser = self.call('/user')['user']
            self.assertEqual(targetId, loggedUser['id'])
            self.assertEqual(0, loggedUser['credit'])

            # accept it
            transaction = self.call('/api/offer/{}/accept'.format(offer['id']), data=None)

            # offer is removed
            self.call('/api/offer/{}/'.format(offer['id']), expectedStatus=404)

            # transaction is created
            self.assertGreater(transaction['id'], -1)
            self.assertEqual(transaction['item'], 'yoghurt')
            self.assertEqual(transaction['amount'], 3)
            self.assertEqual(transaction['price'], 10)
            self.assertEqual(transaction['owner'], ownerId)
            self.assertEqual(transaction['target'], targetId)
            self.assertIsNotNone(transaction['timestamp'])
            self.check_credit(-3*10)
            self.login(ownerEmail)
            self.check_credit(3*10)

    def test_accept_offer_without_target_has_target_in_transaction(self):
        with self.client:
            ownerEmail = 'owner_AOWT@test.com'
            ownerId = self.login(ownerEmail)['id']
            offer = self.createOffer(ownerId, 'tapas', amount=5, price=3)
            self.assertIsNone(offer['target'])
            offerUrl = '/api/offer/{}'.format(offer['id'])

            targetId = self.login('target_AOWT@test.com')['id']
            transaction = self.call(offerUrl + '/accept', amount=2)
            self.assertEqual(transaction['target'], targetId)
            self.assertEqual(transaction['amount'], 2)
            self.check_credit(-2*3)

            remainingOffer = self.call(offerUrl)
            self.assertIsNone(remainingOffer['target'], None)
            self.assertEqual(remainingOffer['amount'], 3)

    def test_partial_accept(self):
        with self.client:
            ownerEmail = 'admin_partial@test.com'
            targetEmail = 'client_partial@test.com'
            ownerId = self.login(ownerEmail)['id']
            targetId = self.createUser(targetEmail)
            offer = self.createOffer(ownerId, 'coffee', amount=500, price=5, targetId=targetId)
            self.login(targetEmail)
            offerUrl = '/api/offer/{}'.format(offer['id'])
            transaction = self.call(offerUrl + '/accept', amount=200)
            self.assertEqual(transaction['amount'], 200)
            self.check_credit(-200*5)
            offer = self.call(offerUrl)
            self.assertEqual(offer['amount'], 300)

            # exhaust
            transaction = self.call(offerUrl + '/accept', amount=300)
            self.assertEqual(transaction['amount'], 300)
            self.call(offerUrl, expectedStatus=404)

            self.login(ownerEmail)
            self.check_credit(5*500)

    def test_accept_by_nontarget_denied(self):
        with self.client:
            ownerEmail = 'admin_denied@test.com'
            ownerId = self.login(ownerEmail)['id']
            targetId = self.createUser('target@test.com')
            offer = self.createOffer(ownerId, 'pizza', amount=1, price=15, targetId=targetId)
            self.login('another@test.com')
            data = self.call('/api/offer/{}/accept'.format(offer['id']), expectedStatus=403, data=None)
            self.check_credit(0)
            self.login(ownerEmail)
            self.check_credit(0)

    def test_accept_without_target(self):
        with self.client:
            ownerId = self.login('admin_AWT@test.com')['id']
            offer = self.createOffer(ownerId, 'pizza', amount=1, price=17)
            self.login('another_AWT@test.com')
            data = self.call('/api/offer/{}/accept'.format(offer['id']), data=None)
            self.check_credit(-17)

    def test_decline(self):
        targetEmail = 'targetDecline@test.com'
        with self.client:
            ownerEmail = 'adminDecline@test.com'
            ownerId = self.login(ownerEmail)['id']
            targetId = self.createUser(targetEmail)
            offer = self.createOffer(ownerId, 'pizza', amount=1, price=15, targetId=targetId)
            offerUrl = '/api/offer/{}'.format(offer['id'])
            self.login(targetEmail)
            self.call(offerUrl + '/decline', expectedStatus=204, data=None)
            data = self.call(offerUrl, expectedStatus=404)

            self.check_credit(0)
            self.login(ownerEmail)
            self.check_credit(0)

    def test_decline_by_nontarget_denied(self):
         with self.client:
            ownerId = self.login('adminDeclineDenied@test.com')['id']
            targetId = self.createUser('targetDeclineDenied@test.com')
            offer = self.createOffer(ownerId, 'pizza', amount=1, price=17, targetId=targetId)
            self.login('anotherDeclineDenied@test.com')
            self.call('/api/offer/{}/decline'.format(offer['id']), expectedStatus=403, data=None)
            self.check_credit(0)
            self.login('targetDeclineDenied@test.com')
            self.check_credit(0)

    def test_remove(self):
        with self.client:
            ownerId = self.login('adminRemove@test.com')['id']
            offer = self.createOffer(ownerId, 'cake', amount=10, price=11)
            offerUrl = '/api/offer/{}'.format(offer['id'])
            self.call(offerUrl + '/remove', expectedStatus=204, data=None)
            data = self.call(offerUrl, expectedStatus=404)
            self.check_credit(0)

    def test_remove_by_target_denied(self):
         with self.client:
            ownerEmail = 'adminRemoveDenied@test.com'
            ownerId = self.login(ownerEmail)['id']
            targetId = self.createUser('anotherRemoveDenied@test.com')
            offer = self.createOffer(ownerId, 'cake', amount=5, price=7, targetId=targetId)
            self.login('anotherRemoveDenied@test.com')
            self.call('/api/offer/{}/remove'.format(offer['id']), expectedStatus=403, data=None)
            self.check_credit(0)
            self.login(ownerEmail)
            self.check_credit(0)

    def test_autoaccept_admin(self):
        with self.client:
            userId = self.login('user_AAA@test.com')['id']
            adminId = self.login(self.adminEmail)['id']
            self.assertEqual(adminId, 1)
            transaction = self.createOffer(adminId, 'fee', amount=1, price=8, targetId=userId)
            self.assertIn('timestamp', transaction)
            self.check_credit(8)

if __name__ == "__main__":
    unittest.main(verbosity=2)
