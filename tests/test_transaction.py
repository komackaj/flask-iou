#!/usr/bin/python3

from datetime import datetime
import unittest

from base import TestBase
from iou.schemas import schemas

# TODO: tests cannot edit

class TransactionTest(TestBase):

    def getTransactionParams(self, item, amount, price, ownerId=None, targetId=None):
        target = targetId or self.login('b@test.com')['id']
        owner = ownerId or self.login('a@test.com')['id']
        return {
                "ownerId" : owner,
                "item"    : item,
                "amount"  : amount,
                "price"   : price,
                'targetId': target,
                'timestamp': datetime.now()
            }

    def createTransaction(self, item, amount, price, ownerId=None, targetId=None):
        params = self.getTransactionParams(item, amount, price, ownerId, targetId)
        return schemas['transaction'].create(params).json

    def test_list(self):
        with self.client:
            ownerId = self.createUser('me@test.com')['id']
            targetId = self.createUser('him@test.com')['id']
            transaction = self.createTransaction('pie', amount=2, price=5, ownerId=ownerId, targetId=targetId)
            self.assertEqual('pie', transaction['item'])

            def check(email):
                self.login(email)
                data = self.call('/api/transaction/')
                self.assertEqual(1, len(data))
                self.assertEqual(transaction, data[0])

            check('me@test.com')
            check('him@test.com')

    def test_cannot_create_transaction_using_api(self):
        with self.client:
            params = self.getTransactionParams('soda', amount=1, price=1)
            self.call('/api/transaction/', expectedStatus=403, **params)


if __name__ == "__main__":
    unittest.main(verbosity=2)
