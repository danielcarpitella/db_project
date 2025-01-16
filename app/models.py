import sqlalchemy as sq
import hashlib
import enum
from sqlalchemy import Integer, String, Enum
from typing import Optional
from sqlalchemy.orm import relationship
from sqlalchemy import ForeignKey
from typing import List
from flask_login import UserMixin, AnonymousUserMixin
from . import db, login_manager

from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask import current_app, request, url_for


class User(UserMixin, db.Model):
    __tablename__ = 'users'                   

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String, nullable=False)
    last_name = db.Column(db.String, nullable=False)
    email = db.Column(db.String, nullable=False, unique=True)
    phone = db.Column(db.String, nullable=True)
    address = db.Column(db.String, nullable=True)
    password_hash = db.Column(db.String, nullable=False)
    created_at = db.Column(sq.TIMESTAMP, nullable=False, server_default=sq.func.now())
    deleted_at = db.Column(sq.TIMESTAMP, nullable=True)
    
    cart = db.relationship('Cart', backref='user', lazy=True, primaryjoin="User.id == foreign(Cart.user_id)")

    @property
    def cart_items_count(self):
        cart = Cart.query.filter_by(user_id=self.id).first()
        if cart:
            return ProductsCart.query.filter_by(cart_id=cart.id).count()
        return 0
    
    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')
    
    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.email}>'
    
    
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
    
class Buyer(db.Model):
    __tablename__ = 'buyers'

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    shipping_address = db.Column(db.String, nullable=False)
    payment_method = db.Column(db.Enum('Card', 'Paypal', 'Klarna', name='payment_method'), default='Card')
    user = relationship('User', backref='buyer', uselist=False)

    def __repr__(self):
        return f'<Buyer {self.user_id}>'


class Seller(db.Model):
    __tablename__ = 'sellers'

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    store_name = db.Column(db.String, nullable=False)
    user = relationship('User', backref='seller', uselist=False)

    def __repr__(self):
        return f'<Seller {self.store_name}>'


class Category(db.Model):
    __tablename__ = 'categories'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    description = db.Column(db.String, nullable=True)
    created_at = db.Column(sq.TIMESTAMP, nullable=False, server_default=sq.func.now())

    def __repr__(self):
        return f'<Category {self.title}>'


class Product(db.Model):
    __tablename__ = 'products'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('sellers.user_id'))
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'))
    name = db.Column(db.String, nullable=False)
    description = db.Column(db.String, nullable=True)
    brand = db.Column(db.String, nullable=True)
    price = db.Column(db.Float, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    created_at = db.Column(sq.TIMESTAMP, nullable=False, server_default=sq.func.now())
    deleted_at = db.Column(sq.TIMESTAMP, nullable=True)

    seller = relationship('Seller', backref='products')
    category = relationship('Category', backref='products')

    def __repr__(self):
        return f'<Product {self.name}>'


class Cart(db.Model):
    __tablename__ = 'carts'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('buyers.user_id'))

    buyer = relationship('Buyer', backref='cart')
    products = db.relationship('ProductsCart', backref='cart_products', lazy=True)
    
    @property
    def cart_items_count(self):
        return ProductsCart.query.filter_by(cart_id=self.id).count()
    
    def __repr__(self):
        return f'<Cart {self.id}>'


class Order(db.Model):
    __tablename__ = 'orders'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('buyers.user_id'))
    total = db.Column(db.Float) 
    shipping_address = db.Column(db.String)
    payment_method = db.Column(db.Enum('Card', 'Paypal', 'Klarna', name='payment_method'), default='Card')
    created_at = db.Column(sq.TIMESTAMP, nullable=False, server_default=sq.func.now())

    buyer = relationship('Buyer', backref='orders')

    def __repr__(self):
        return f'<Order {self.id}>'


class Review(db.Model):
    __tablename__ = 'reviews'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('buyers.user_id'))
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'))
    rate = db.Column(db.Integer, nullable=False)
    title = db.Column(db.String, nullable=False)
    description = db.Column(db.String, nullable=True)
    created_at = db.Column(sq.TIMESTAMP, nullable=False, server_default=sq.func.now())
    updated_at = db.Column(sq.TIMESTAMP, nullable=True)
    deleted_at = db.Column(sq.TIMESTAMP, nullable=True)

    buyer = relationship('Buyer', backref='reviews')
    product = relationship('Product', backref='reviews')

    def __repr__(self):
        return f'<Review {self.title}>'


class ProductOrderQuantity(db.Model):
    __tablename__ = 'product_order_quantity'

    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), primary_key=True)
    quantity = db.Column(db.Integer, nullable=False)

    product = relationship('Product', backref='order_quantities')
    order = relationship('Order', backref='product_quantities')

    def __repr__(self):
        return f'<ProductOrderQuantity {self.product_id}, {self.order_id}>'


class ProductsCart(db.Model):
    __tablename__ = 'products_cart'

    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), primary_key=True)
    cart_id = db.Column(db.Integer, db.ForeignKey('carts.id'), primary_key=True)
    quantity = db.Column(db.Integer, nullable=False)
    
    product = relationship('Product', backref='cart_products')
    cart = relationship('Cart', backref='cart_items')

    def __repr__(self):
        return f'<ProductsCart {self.product_id}, {self.cart_id}>'
    
    
class SellerOrder(db.Model):
    __tablename__ = 'sellers_orders'

    order_id = db.Column(db.Integer, primary_key=True)
    seller_id = db.Column(db.Integer, db.ForeignKey('sellers.user_id'))
    buyer_order_id = db.Column(db.Integer, db.ForeignKey('orders.id'))
    order_status = db.Column(db.Enum('Pending', 'Shipped', 'Delivered', name='order_status'), nullable=False, default='Pending')
    
    created_at = db.Column(sq.TIMESTAMP, nullable=False, server_default=sq.func.now())
    deleted_at = db.Column(sq.TIMESTAMP, nullable=True)

    seller = relationship('Seller', backref='sellers_orders')
    order = relationship('Order', backref='sellers_orders')

    def __repr__(self):
        return f'<SellersOrders {self.order_id}, {self.seller_id}, {self.buyer_order_id}>'