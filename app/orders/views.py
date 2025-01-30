from flask import render_template, redirect, url_for, flash, request, session, abort
from flask_login import login_required, current_user
from app.orders import orders
from app.models import Order, Product, Cart, ProductsCart, SellerOrder, ProductOrderQuantity, Buyer, User
from app import db
from .forms import ShippingForm
from app.decorators import buyer_required, seller_required


@orders.route('/checkout/shipping', methods=['GET', 'POST'])
@buyer_required
def checkout_shipping():
    
    cart = Cart.query.filter_by(user_id=current_user.id).first()
    if not cart or not cart.products:
        flash('Your cart is empty. Please add products to your cart before proceeding to checkout.', 'danger')
        return redirect(url_for('cart.cart_view')) 
    
    # Verifica la disponibilità dei prodotti nel carrello
    for product_cart in cart.products:
        product = Product.query.get(product_cart.product_id)
        if product and product_cart.quantity > product.quantity:
            flash(f'Not enough stock for product {product.name}. Available: {product.quantity}, Requested: {product_cart.quantity}', 'danger')
            return redirect(url_for('cart.cart_view'))
    
    buyer = Buyer.query.filter_by(user_id=current_user.id).first()
    saved_address = buyer.shipping_address if buyer else None
    
    if request.method == 'POST':
        if 'proceed_to_payment' in request.form:
            return redirect(url_for('orders.checkout_payment', shipping_address=saved_address))
    
    return render_template('checkout_shipping.html', saved_address=saved_address)
 
 
@orders.route('/checkout/shipping/address', methods=['GET', 'POST'])
@buyer_required
def checkout_shipping_address():
    form = ShippingForm()
    
    if form.validate_on_submit():
        shipping_address = f"{form.address.data}, {form.city.data}, {form.zip_code.data}, {form.country.data}"
        return redirect(url_for('orders.checkout_payment', shipping_address=shipping_address))
    
    return render_template('checkout_shipping_address.html', form=form)

       
@orders.route('/checkout/payment', methods=['GET', 'POST'])
@buyer_required
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
            
            
            '''
            Update the product quantity, if the quantity in the order 
            is greater than the number of available orders, an error is returned
            '''
            product = Product.query.get(product_cart.product_id)
            if product:
                product.quantity -= product_cart.quantity
                if product.quantity < 0:
                    flash(f'Not enough stock for product {product.name}', 'danger')
                    return redirect(url_for('cart.cart_view'))
                
            
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
@buyer_required
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


@orders.route('/orders')
@buyer_required
def buyer_orders():
    orders = Order.query.filter_by(user_id=current_user.id).order_by(Order.created_at.desc()).all()
    seller_orders = SellerOrder.query.filter(SellerOrder.buyer_order_id.in_([order.id for order in orders])).all()
    
    orders_dict = {}
    for order in orders:
        orders_dict[order.id] = {
            'order': order,
            'seller_orders': [so for so in seller_orders if so.buyer_order_id == order.id]
        }
    
    return render_template('orders.html', orders=orders_dict)


@orders.route('/orders/<int:store_order_id>')
@buyer_required
def store_order_detail(store_order_id):
    
    store_order = SellerOrder.query.get_or_404(store_order_id)
    
    # Verifies that the order belongs to the current user 
    buyer_order = Order.query.get(store_order.buyer_order_id)
    if buyer_order.user_id != current_user.id:
        abort(403)
    
    products_ordered = ProductOrderQuantity.query.filter_by(order_id=store_order.buyer_order_id).all()
    products_ordered = [po for po in products_ordered if po.product.user_id == store_order.seller_id]    
    
    return render_template('order_details.html', store_order=store_order, products_ordered=products_ordered)


@orders.route('/seller/orders')
@seller_required
def seller_orders():
    if not current_user.seller:
        abort(403)
    
    seller_orders = SellerOrder.query.filter_by(seller_id=current_user.id).order_by(SellerOrder.created_at.desc()).all()
    
    orders_list = []
    for seller_order in seller_orders:
        buyer_order = Order.query.get(seller_order.buyer_order_id)
        
        orders_list.append({
            'order_id': seller_order.order_id,
            'created_at': buyer_order.created_at,
            'order_status': seller_order.order_status,
            'buyer_name': buyer_order.buyer.user.first_name
        })
    
    return render_template('sellers_orders.html', orders=orders_list)


@orders.route('/seller/orders/<int:order_id>', methods=['GET', 'POST'])
@seller_required
def seller_order_detail(order_id):
    seller_order = SellerOrder.query.get_or_404(order_id)
    
    if seller_order.seller_id != current_user.id:
        abort(403)
    
    if request.method == 'POST':
        new_status = request.form.get('order_status')
        if new_status in ['Pending', 'Shipped', 'Delivered']:
            seller_order.order_status = new_status
            db.session.commit()
            flash('Order status updated successfully.', 'success')
        else:
            flash('Invalid order status.', 'danger')
    
    buyer_order = Order.query.get(seller_order.buyer_order_id)
    products_ordered = ProductOrderQuantity.query.filter_by(order_id=seller_order.buyer_order_id).all()
    products_ordered = [po for po in products_ordered if po.product.user_id == seller_order.seller_id]
    
    return render_template('sellers_orders_details.html', seller_order=seller_order, buyer_order=buyer_order, products_ordered=products_ordered)

