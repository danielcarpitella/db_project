from flask import render_template, request, abort, url_for, redirect, flash 
from . import main
from app.models import Product, Category, Review, Cart, ProductsCart, Seller, Order, ProductOrderQuantity, User, SellerOrder, Buyer
from flask_login import current_user, login_required
from app import db
from .forms import EditProfileForm


@main.route('/')
def index():
    return render_template('index.html')


@main.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(id=username).first_or_404()
    return render_template('user.html', user=user)


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







