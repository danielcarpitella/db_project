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

#usato nella single product page
@cart.route('/cart/add', methods=['POST'])
@login_required
def add_to_cart():
    try:
        product_id = request.form.get('product_id')
        if not product_id:
            flash('Product ID is required', 'danger')
            return redirect(url_for('products.single_product', product_id=product_id))
        
        product = Product.query.get(product_id)
        if not product:
            flash('Product not found', 'danger')
            return redirect(url_for('products.single_product', product_id=product_id))
        
        cart = Cart.query.filter_by(user_id=current_user.id).first()
        if not cart:
            cart = Cart(user_id=current_user.id)
            db.session.add(cart)
            db.session.commit()
        
        product_cart = ProductsCart.query.filter_by(cart_id=cart.id, product_id=product_id).first()
        if product_cart:
            flash('Product already in cart', 'info')
            return redirect(url_for('cart.cart_view'))

        product_cart = ProductsCart(cart_id=cart.id, product_id=product_id, quantity=1)
        db.session.add(product_cart)
        db.session.commit()

        flash('Product added to cart', 'success')
        return redirect(url_for('cart.cart_view'))
    except Exception as e:
        # Log the error for debugging
        print(f"Error: {e}")
        flash('Internal Server Error', 'danger')
        return redirect(url_for('products.single_product', product_id=product_id))
    
    
@cart.route('/cart/update', methods=['POST'])
@login_required
def update_cart():
    product_id = request.form.get('product_id')
    quantity = request.form.get('quantity')
    
    if not product_id or not quantity:
        flash('Product ID and quantity are required', 'danger')
        return redirect(url_for('cart.cart_view'))
    
    cart = Cart.query.filter_by(user_id=current_user.id).first()
    if not cart:
        flash('Cart not found', 'danger')
        return redirect(url_for('cart.cart_view'))
    
    product_cart = ProductsCart.query.filter_by(cart_id=cart.id, product_id=product_id).first()
    if product_cart:
        product_cart.quantity = quantity
        db.session.commit()
        flash('Cart updated successfully', 'success')
    else:
        flash('Product not found in cart', 'danger')
    
    return redirect(url_for('cart.cart_view'))


@cart.route('/cart/remove', methods=['POST'])
@login_required
def remove_from_cart():
    product_id = request.form.get('product_id')
    
    if not product_id:
        flash('Product ID is required', 'danger')
        return redirect(url_for('cart.cart_view'))
    
    cart = Cart.query.filter_by(user_id=current_user.id).first()
    if not cart:
        flash('Cart not found', 'danger')
        return redirect(url_for('cart.cart_view'))
    
    product_cart = ProductsCart.query.filter_by(cart_id=cart.id, product_id=product_id).first()
    if product_cart:
        db.session.delete(product_cart)
        db.session.commit()
        flash('Product removed from cart', 'success')
    else:
        flash('Product not found in cart', 'danger')
    
    return redirect(url_for('cart.cart_view'))