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
            loggedIn = self.call('/user')['user']['id']
            self.assertEqual(targetId, loggedIn)

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

            # TODO: check credit

    def test_partial_accept(self):
         with self.client:
            targetEmail = 'client@test.com'
            ownerId = self.login('admin@test.com')['id']
            targetId = self.createUser(targetEmail)
            offer = self.createOffer(ownerId, 'coffee', amount=500, price=5, targetId=targetId)
            self.login(targetEmail)
            offerUrl = '/api/offer/{}'.format(offer['id'])
            transaction = self.call(offerUrl + '/accept', amount=200)
            self.assertEqual(transaction['amount'], 200)
            offer = self.call(offerUrl)
            self.assertEqual(offer['amount'], 300)

    def test_accept_by_nontarget_denied(self):
         with self.client:
            ownerId = self.login('admin@test.com')['id']
            targetId = self.createUser('target@test.com')
            offer = self.createOffer(ownerId, 'pizza', amount=1, price=15, targetId=targetId)
            self.login('another@test.com')
            data = self.call('/api/offer/{}/accept'.format(offer['id']), expectedStatus=403, data=None)

    def test_decline(self):
        targetEmail = 'targetDecline@test.com'
        with self.client:
            ownerId = self.login('adminDecline@test.com')['id']
            targetId = self.createUser(targetEmail)
            offer = self.createOffer(ownerId, 'pizza', amount=1, price=15, targetId=targetId)
            offerUrl = '/api/offer/{}'.format(offer['id'])
            self.login(targetEmail)
            self.call(offerUrl + '/decline', expectedStatus=204, data=None)
            data = self.call(offerUrl, expectedStatus=404)

    def test_decline_by_nontarget_denied(self):
         with self.client:
            ownerId = self.login('adminDeclineDenied@test.com')['id']
            targetId = self.createUser('targetDeclineDenied@test.com')
            offer = self.createOffer(ownerId, 'pizza', amount=1, price=17, targetId=targetId)
            self.login('anotherDeclineDenied@test.com')
            self.call('/api/offer/{}/decline'.format(offer['id']), expectedStatus=403, data=None)

if __name__ == "__main__":
    unittest.main(verbosity=2)
