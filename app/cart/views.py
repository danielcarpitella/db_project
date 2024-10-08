from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.cart import cart
from app.models import Cart, ProductsCart, Product
from app import db


@cart.route('/cart')
@login_required
def cart_view():
    cart = Cart.query.filter_by(user_id=current_user.id).first()
    if not cart or not cart.products:
        return render_template('cart.html', products=[])
    
    products_cart = ProductsCart.query.filter_by(cart_id=cart.id).all()
    products = []
    for item in products_cart:
        product = Product.query.get(item.product_id)
        products.append({
            'product': product,
            'quantity': item.quantity
        })
    
    return render_template('cart.html', products=products)





