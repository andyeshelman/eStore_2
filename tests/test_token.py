from faker import Faker

import unittest
from unittest.mock import MagicMock, patch

from app import app

fake = Faker()

class TestTokenEndpoint(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        self.client = app.test_client()
    
    @patch('app.routes.encode_token')
    @patch('app.routes.db.session.scalar')
    @patch('app.routes.check_password_hash')
    def test_successful_authenticate(self, mock_check_hash, mock_scalar, mock_encode_token):
        mock_customer = MagicMock()
        mock_customer.id = 123

        mock_scalar.return_value = mock_customer
        mock_check_hash.return_value = True
        mock_encode_token.return_value = "some random nonsense"

        request_body = {
            'username': fake.user_name(),
            'password': fake.password()
        }

        response = self.client.post('/token', json=request_body)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['token'], "some random nonsense")

    def test_unauthorized_user(self):
        request_body = {
            'username': fake.user_name(),
            'password': fake.password()
        }

        response = self.client.post('/token', json=request_body)
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json['token'], "Password is incorrect...")