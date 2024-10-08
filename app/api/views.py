from flask import request, jsonify
from .import api
from app import db, jwt
from ..models import Product, Cart, ProductsCart, User
from sqlalchemy import desc
from .serializer import serialize_paginated_products, serialize_product
from flask_login import current_user
from werkzeug.security import check_password_hash
from flask_login import login_user, current_user, login_required, logout_user


@api.route('/login', methods=['POST'])
def login():
    email = request.json.get('email')
    password = request.json.get('password')
    
    if not email or not password:
        return jsonify({'error': 'Email and password are required'}), 400

    user = User.query.filter_by(email=email).first()
    if user and check_password_hash(user.password_hash, password):
        login_user(user, remember=False)
        return jsonify({'message': 'Logged in successfully'}), 200
    else:
        return jsonify({'error': 'Invalid email or password'}), 401
  

@api.route('/products', methods=['GET'])
def get_products():
    page = request.args.get('page', 1, type=int)
    page_size = request.args.get('page_size', 5, type=int)
    search = request.args.get('search', '', type=str)
    category = request.args.get('category', '', type=str)

    products_query = Product.query.order_by(Product.created_at.desc())

    if search:
        products_query = products_query.filter(Product.name.ilike(f'%{search}%'))
    
    if category:
        products_query = products_query.filter(Product.category_id == category)

    paginated_products = products_query.paginate(page=page, per_page=page_size, error_out=False)
    response = serialize_paginated_products(paginated_products)

    return jsonify(response)


@api.route('/cart', methods=['PUT'])
@login_required
def update_cart():
    data = request.get_json()
    product_id = data.get('product_id')
    quantity = data.get('quantity')
    
    cart = Cart.query.filter_by(user_id=current_user.id).first()
    if not cart:
        return jsonify({'error': 'Cart not found'}), 404
    
    product_cart = ProductsCart.query.filter_by(cart_id=cart.id, product_id=product_id).first()
    if product_cart:
        product_cart.quantity = quantity
        db.session.commit()
        return jsonify({'message': 'Cart updated successfully'})
    return jsonify({'error': 'Product not found in cart'}), 404


@api.route('/cart', methods=['DELETE'])
@login_required
def remove_from_cart():
    data = request.get_json()
    product_id = data.get('product_id')
    
    cart = Cart.query.filter_by(user_id=current_user.id).first()
    if not cart:
        return jsonify({'error': 'Cart not found'}), 404
    
    product_cart = ProductsCart.query.filter_by(cart_id=cart.id, product_id=product_id).first()
    if product_cart:
        db.session.delete(product_cart)
        db.session.commit()
        return jsonify({'message': 'Product removed from cart'})
    return jsonify({'error': 'Product not found in cart'}), 404


@api.route('/cart', methods=['POST'])    
@login_required
def add_to_cart():
   try:
        product_id = request.json.get('product_id')
        if not product_id:
            return jsonify({'error': 'Product ID is required'}), 400
        
        product = Product.query.get(product_id)
        if not product:
            return jsonify({'error': 'Product not found'}), 404
        
        cart = Cart.query.filter_by(user_id=current_user.id).first()
        if not cart:
            cart = Cart(user_id=current_user.id)
            db.session.add(cart)
            db.session.commit()
        
        product_cart = ProductsCart.query.filter_by(cart_id=cart.id, product_id=product_id).first()
        if product_cart:
            return jsonify({'message': 'Product already in cart'}), 200

        product_cart = ProductsCart(cart_id=cart.id, product_id=product_id, quantity=1)
        db.session.add(product_cart)
        db.session.commit()

        return jsonify({'message': 'Product added to cart'}), 200
   except Exception as e:
        # Log the error for debugging
        print(f"Error: {e}")
        return jsonify({'error': 'Internal Sserver Error'}), 500
    