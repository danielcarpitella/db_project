from flask import render_template, redirect, url_for, flash, request, session, abort
from flask_login import login_required, current_user
from app.orders import orders
from app.models import Order, Product, Cart, ProductsCart, SellerOrder, ProductOrderQuantity, Buyer
from app import db
from .forms import ShippingForm


@orders.route('/checkout/shipping', methods=['GET', 'POST'])
@login_required
def checkout_shipping():
    
    cart = Cart.query.filter_by(user_id=current_user.id).first()
    if not cart or not cart.products:
        flash('Your cart is empty. Please add products to your cart before proceeding to checkout.', 'danger')
        return redirect(url_for('cart.cart_view')) 
    
    buyer = Buyer.query.filter_by(user_id=current_user.id).first()
    saved_address = buyer.shipping_address if buyer else None
    
    if request.method == 'POST':
        if 'proceed_to_payment' in request.form:
            return redirect(url_for('orders.checkout_payment', shipping_address=saved_address))
    
    return render_template('checkout_shipping.html', saved_address=saved_address)
 
 
@orders.route('/checkout/shipping/address', methods=['GET', 'POST'])
@login_required
def checkout_shipping_address():
    form = ShippingForm()
    
    if form.validate_on_submit():
        shipping_address = f"{form.address.data}, {form.city.data}, {form.zip_code.data}, {form.country.data}"
        return redirect(url_for('orders.checkout_payment', shipping_address=shipping_address))
    
    return render_template('checkout_shipping_address.html', form=form)

       
@orders.route('/checkout/payment', methods=['GET', 'POST'])
@login_required
def checkout_payment():
    shipping_address = request.args.get('shipping_address')
    if not shipping_address:
        flash('shipping address not found', 'danger')
        return redirect(url_for('orders.checkout_shipping'))
    
    if request.method == 'POST':
        payment_method = request.form.get('payment_method')
        if not payment_method:
            flash('Please select a payment method.', 'danger')
            return redirect(url_for('orders.checkout_payment', shipping_address=shipping_address))
        
        cart = Cart.query.filter_by(user_id=current_user.id).first()
        if not cart or not cart.products:
            flash('Your cart is empty.', 'danger')
            return redirect(url_for('main.index'))
        
        total_amount = sum(product_cart.product.price * product_cart.quantity for product_cart in cart.products)
        
        order = Order(
            user_id=current_user.id,
            shipping_address=shipping_address,
            total=total_amount,
            payment_method=payment_method
        )
        db.session.add(order)
        db.session.commit()
        
        seller_orders = {}
        
        for product_cart in cart.products:
            product_order_quantity = ProductOrderQuantity(
                order_id=order.id,
                product_id=product_cart.product_id,
                quantity=product_cart.quantity
            )
            db.session.add(product_order_quantity)
            
            seller_id = product_cart.product.user_id
            if seller_id not in seller_orders:
                seller_order = SellerOrder(
                    seller_id=seller_id,
                    buyer_order_id=order.id,
                    order_status='Pending'
                )
                db.session.add(seller_order)
                db.session.flush()   #Ensure the seller_order.id is available
                seller_orders[seller_id] = seller_order.order_id
        
        for product_cart in cart.products:
            db.session.delete(product_cart)
        db.session.delete(cart)
        db.session.commit()
        
        return redirect(url_for('orders.checkout_confirmation', order_id=order.id))
    
    return render_template('checkout_payment.html', shipping_address=shipping_address)
        
        
@orders.route('/checkout/confirmation', methods=['GET'])
@login_required
def checkout_confirmation():
    order_id = request.args.get('order_id')
    if not order_id:
        flash('No order found.', 'danger')
        return redirect(url_for('main.index'))
    
    order = Order.query.get(order_id)
    if not order or order.user_id != current_user.id:
        flash('Order not found.', 'danger')
        return redirect(url_for('main.index'))
    
    products_ordered = ProductOrderQuantity.query.filter_by(order_id=order_id).all()
    
    return render_template('checkout_confirmation.html', order=order, products_ordered=products_ordered)


@orders.route('/seller/orders')
@login_required
def seller_orders():
    if not current_user.seller:
        abort(403)
    
