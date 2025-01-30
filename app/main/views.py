from flask import render_template, request, abort, url_for, redirect, flash 
from . import main
from app.models import Product, Category, Review, Cart, ProductsCart, Seller, Order, ProductOrderQuantity, User, SellerOrder, Buyer
from flask_login import current_user, login_required
from app import db
from .forms import EditProfileForm, EditSellerProfileForm
from app.decorators import seller_required, buyer_required


@main.route('/')
def index():
    return render_template('index.html')


@main.route('/user/<username>')
@buyer_required
def user(username):
    user = User.query.filter_by(id=username).first_or_404()
    is_buyer = Buyer.query.filter_by(user_id=user.id).first() is not None
    is_seller = Seller.query.filter_by(user_id=user.id).first() is not None

    return render_template('user.html', user=user, is_buyer=is_buyer, is_seller=is_seller)


@main.route('/seller/user/<int:user_id>')
@seller_required
def user_seller(user_id):
    user = User.query.get_or_404(user_id)
    is_buyer = Buyer.query.filter_by(user_id=user.id).first() is not None
    is_seller = Seller.query.filter_by(user_id=user.id).first() is not None

    return render_template('user_seller.html', user=user, is_buyer=is_buyer, is_seller=is_seller)


@main.route('/edit-profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    buyer = Buyer.query.filter_by(user_id=current_user.id).first()
    if not buyer:
        abort(403)
    
    form = EditProfileForm(obj=current_user)
    if form.validate_on_submit():
        current_user.first_name = form.first_name.data
        current_user.last_name = form.last_name.data
        current_user.email = form.email.data
        current_user.phone = form.phone.data
        buyer.shipping_address = form.shipping_address.data
        buyer.payment_method = form.payment_method.data
        db.session.commit()
        flash('Profile updated successfully.', 'success')
        return redirect(url_for('main.user', username=current_user.id))
    
    form.shipping_address.data = buyer.shipping_address
    form.payment_method.data = buyer.payment_method
    
    return render_template('edit_profile.html', form=form)


@main.route('/seller/edit-profile', methods=['GET', 'POST'])
@seller_required
def seller_edit_profile():
    seller = Seller.query.filter_by(user_id=current_user.id).first()
    if not seller:
        abort(403)
    
    form = EditSellerProfileForm(obj=current_user)
    if form.validate_on_submit():
        current_user.first_name = form.first_name.data
        current_user.last_name = form.last_name.data
        current_user.email = form.email.data
        current_user.phone = form.phone.data
        seller.store_name = form.store_name.data
        db.session.commit()
        flash('Profile updated successfully.', 'success')
        return redirect(url_for('main.user_seller', user_id=current_user.id))
    
    form.store_name.data = seller.store_name
    
    return render_template('seller_edit_profile.html', form=form)





