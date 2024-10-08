from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.products import products
from ..models import Product, Category, Review
from app import db


@products.route('/products')
def all_products():
    search = request.args.get('search', '', type=str)
    category_id = request.args.get('category', None, type=int)
    
    products_query = Product.query.order_by(Product.created_at.desc())
    
    if search:
        products_query = products_query.filter(Product.name.ilike(f'%{search}%'))
    
    if category_id:
        products_query = products_query.filter(Product.category_id == category_id)
    
    products = products_query.limit(5).all()
    categories = Category.query.all()
    
    return render_template('products.html', products=products, categories=categories)



@products.route('/product/<int:product_id>')
def single_product(product_id):
    product = Product.query.get_or_404(product_id)
    reviews = Review.query.filter_by(product_id=product_id).all()
    return render_template('singleproduct.html', product=product, reviews=reviews)


