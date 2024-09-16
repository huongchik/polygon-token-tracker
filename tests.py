import unittest
from flask import json
from server import app


class FlaskTestCase(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    # Тест для маршрута /get_balance
    def test_get_balance(self):
        response = self.app.get(
            '/get_balance?address=0x51f1774249Fc2B0C2603542Ac6184Ae1d048351d')
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertIn('balance', data)
        self.assertIn('symbol', data)

    # Тест на отсутствие параметра address
    def test_get_balance_no_address(self):
        response = self.app.get('/get_balance')
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 400)
        self.assertIn('error', data)

    # Тест для маршрута /get_balance_batch
    def test_get_balance_batch(self):
        addresses = {
            "addresses": [
                "0x51f1774249Fc2B0C2603542Ac6184Ae1d048351d",
                "0x4830AF4aB9cd9E381602aE50f71AE481a7727f7C"
            ]
        }
        response = self.app.post(
            '/get_balance_batch', data=json.dumps(addresses), content_type='application/json')
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(data), 2)
        self.assertIn('address', data[0])
        self.assertIn('balance', data[0])
        self.assertIn('symbol', data[0])

    # Тест на некорректный запрос в /get_balance_batch
    def test_get_balance_batch_invalid(self):
        response = self.app.post(
            '/get_balance_batch', data=json.dumps({}), content_type='application/json')
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 400)
        self.assertIn('error', data)

    # Тест для маршрута /get_top_with_transactions
    def test_get_top_with_transactions(self):
        response = self.app.get(
            '/get_top_with_transactions?N=3&token_address=0x1a9b54a3075119f1546c52ca0940551a6ce5d2d0')
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(data), 3)
        self.assertIn('address', data[0])
        self.assertIn('balance', data[0])
        self.assertIn('last_transaction', data[0])

    # Тест на отсутствие параметра N в /get_top_with_transactions
    def test_get_top_with_transactions_no_n(self):
        response = self.app.get(
            '/get_top_with_transactions?token_address=0x1a9b54a3075119f1546c52ca0940551a6ce5d2d0')
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 400)
        self.assertIn('error', data)

    # Тест на отсутствие параметра token_address в /get_top_with_transactions
    def test_get_top_with_transactions_no_token_address(self):
        response = self.app.get('/get_top_with_transactions?N=3')
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 400)
        self.assertIn('error', data)

    # Тест для /get_token_info
    def test_get_token_info(self):
        response = self.app.get(
            '/get_token_info?token_address=0x1a9b54a3075119f1546c52ca0940551a6ce5d2d0')
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertIn('symbol', data)
        self.assertIn('name', data)
        self.assertIn('totalSupply', data)

    # Тест на отсутствие параметра token_address в /get_token_info
    def test_get_token_info_no_address(self):
        response = self.app.get('/get_token_info')
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 400)
        self.assertIn('error', data)


if __name__ == '__main__':
    unittest.main()
