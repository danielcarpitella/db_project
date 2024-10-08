from flask import render_template, request, abort, url_for, redirect, flash 
from . import main
from app.models import Product, Category, Review, Cart, ProductsCart, Seller, Order, ProductOrderQuantity, User, SellerOrder
from flask_login import current_user, login_required
from app import db
from flask import session


@main.route('/')
def index():
    return render_template('index.html')


@main.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(id=username).first_or_404()
    return render_template('user.html', user=user)










