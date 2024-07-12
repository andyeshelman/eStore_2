from app import app, db, limiter, cache
from flask import request, redirect
from werkzeug.security import generate_password_hash, check_password_hash
from app.schemas.customerSchema import (
    customer_input_schema, customer_output_schema,
    customers_schema, customer_login_schema
)
from app.schemas.productSchema import (
    product_schema,
    products_schema
)
from marshmallow import ValidationError
from app.models import Customer, Product
from app.utils.util import encode_token
from app.auth import token_auth

@app.route('/')
def index():
    return redirect('/api/docs/')

@app.post('/token')
def post_token():
    if not request.is_json:
        return {'error': "Request body must be application/json"}, 400
    try:
        credentials = customer_login_schema.load(request.json)
    except ValidationError as err:
        return err.messages, 400
    query = db.select(Customer).filter_by(username=credentials['username'])
    customer = db.session.scalar(query)
    if customer is None:
        return {'error': "Username not found..."}, 404
    if not check_password_hash(customer.password, credentials['password']):
        return {'error': "Password is incorrect..."}, 401
    auth_token = encode_token(customer.id)
    return {'token': auth_token}

@app.get('/customers')
def get_all_customers():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    search = request.args.get('search')
    query = db.select(Customer).limit(per_page).offset((page-1)*per_page)
    if search:
        query = query.where(Customer.username.like(f'%{search}%'))
    customers = db.session.scalars(query).all()
    return customers_schema.jsonify(customers)

@app.get('/customers/<int:customer_id>')
@cache.cached(timeout=60)
def get_one_customer(customer_id):
    customer = db.session.get(Customer, customer_id)
    if customer:
        return customer_output_schema.jsonify(customer)
    else:
        return {'error': f"No customer with ID {customer_id} exists..."}, 404

@app.post('/customers')
def post_customer():
    if not request.is_json:
        return {'error': "Request body must be application/json"}, 400
    try:
        customer_data = customer_input_schema.load(request.json)
        query = db.select(Customer).where( (Customer.username == customer_data['username']) | (Customer.email == customer_data['email']) )
        dupe = db.session.scalar(query)
        if dupe is not None:
            return {'error': "Customer with that username and/or email already exists"}, 400
        new_customer = Customer(**customer_data)
        new_customer.password = generate_password_hash(new_customer.password)
        db.session.add(new_customer)
        db.session.commit()
        return customer_output_schema.jsonify(new_customer), 201
    except ValidationError as err:
        return err.messages, 400
    
@app.get('/products')
@limiter.limit("100 per hour, 1 per sec")
def get_all_products():
    args = request.args
    page = args.get('page', 1, type=int)
    per_page = args.get('per_page', 10, type=int)
    search = args.get('search')
    query = db.select(Product).limit(per_page).offset((page-1)*per_page)
    if search:
        query = query.where(Product.name.like(f'%{search}%'))
    products = db.session.scalars(query).all()
    return products_schema.jsonify(products)

@app.get('/products/<int:product_id>')
def get_one_product(product_id):
    product = db.session.get(Product, product_id)
    if product:
        return product_schema.jsonify(product)
    else:
        return {'error': f"No product with ID {product_id} exists..."}, 404
    
@app.post('/products')
@token_auth.login_required
def post_product():
    if not request.is_json:
        return {'error': "Request body must be application/json"}, 400
    try:
        product_data = product_schema.load(request.json)
    except ValidationError as err:
        return err.messages, 400
    new_product = Product(**product_data)
    db.session.add(new_product)
    db.session.commit()
    return product_schema.jsonify(new_product), 201