from flask_httpauth import HTTPTokenAuth

from app.utils.util import decode_token
from app.models import Customer
from app.database import db

token_auth = HTTPTokenAuth()

@token_auth.verify_token
def verify(token):
    customer_id = decode_token(token)
    if customer_id is None:
        return None
    return db.session.get(Customer, customer_id)

@token_auth.error_handler
def handle_error(status):
    return {'error': "Invalid token..."}, status