from flask import render_template, request, redirect, url_for, flash, session
from app import db
from .. models import User, Buyer, Seller
from .forms import RegistrationForm, LoginForm
from . import auth
from werkzeug.security import generate_password_hash
from flask_login import login_user, logout_user, login_required, current_user

@auth.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        session['registration_data'] = {
            'first_name': form.first_name.data,
            'last_name': form.last_name.data,
            'email': form.email.data,
            'phone': form.phone.data,
            'address': form.address.data,
            'password': form.password.data
        }
        flash('Personal information saved. Please choose your user type.')
        return redirect(url_for('auth.register_user_type'))
    return render_template('auth/register.html', form=form)
    
    
@auth.route('/register/user-type', methods=['GET', 'POST'])
def register_user_type():
    if request.method == 'POST':
        user_type = request.form.get('user_type')
        session['user_type'] = user_type
        if user_type == 'buyer':
            return redirect(url_for('auth.buyer_registration'))
        elif user_type == 'seller':
            return redirect(url_for('auth.seller_registration'))
        else:
            flash('Invalid user type selected.')
    return render_template('auth/register_user_type.html')

    
@auth.route('/register/user-type/buyer', methods=['GET', 'POST'])
def buyer_registration():
    if request.method == 'POST':
        registration_data = session.get('registration_data')
        if not registration_data:
            flash('Registration data not found. Please start over.')
            return redirect(url_for('auth.register'))
        
        shipping_address = request.form.get('shipping_address')
        payment_method = request.form.get('payment_method')
        
        user = User(
            first_name=registration_data['first_name'],
            last_name=registration_data['last_name'],
            email=registration_data['email'],
            phone=registration_data['phone'],
            address=registration_data['address'],
            password=registration_data['password']
        )
        db.session.add(user)
        db.session.commit()
        
        buyer = Buyer(
            user_id=user.id,
            shipping_address=shipping_address,
            payment_method=payment_method
        )
        db.session.add(buyer)
        db.session.commit()
        
        flash('Registration complete. You can now log in.')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/register_user-type_buyer.html')


@auth.route('/register/user-type/seller', methods=['GET', 'POST'])
def seller_registration():
    if request.method == 'POST':
        registration_data = session.get('registration_data')
        if not registration_data:
            flash('Registration data not found. Please start over.')
            return redirect(url_for('auth.register'))
        
        store_name = request.form.get('store_name')
        
        user = User(
            first_name=registration_data['first_name'],
            last_name=registration_data['last_name'],
            email=registration_data['email'],
            phone=registration_data['phone'],
            address=registration_data['address'],
            password=registration_data['password']
        )
        db.session.add(user)
        db.session.commit()
        
        seller = Seller(
            user_id=user.id,
            store_name=store_name
        )
        db.session.add(seller)
        db.session.commit()
        
        flash('Registration complete. You can now log in.')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/register_user-type_seller.html')
   
   
@auth.route('/add-user-type/seller', methods=['GET', 'POST'])
@login_required
def add_user_type_seller():
    is_buyer = Buyer.query.filter_by(user_id=current_user.id).first() is not None
    is_seller = Seller.query.filter_by(user_id=current_user.id).first() is not None

    if is_seller:
        flash('You are already a seller.')
        return redirect(url_for('main.user', username=current_user.username))

    if request.method == 'POST':
        store_name = request.form.get('store_name')
        
        seller = Seller(
            user_id=current_user.id,
            store_name=store_name
        )
        db.session.add(seller)
        db.session.commit()
        
        flash('You have also become a seller, please login again')
        logout_user()  
        return redirect(url_for('auth.login'))  
    
    return render_template('auth/add_user_type_seller.html', is_buyer=is_buyer)


@auth.route('/add-user-type/buyer', methods=['GET', 'POST'])
@login_required
def add_user_type_buyer():
    is_seller = Seller.query.filter_by(user_id=current_user.id).first() is not None
    is_buyer = Buyer.query.filter_by(user_id=current_user.id).first() is not None

    if is_buyer:
        flash('You are already a buyer.')
        return redirect(url_for('main.user_seller', user_id=current_user.id))

    if request.method == 'POST':
        shipping_address = request.form.get('shipping_address')
        payment_method = request.form.get('payment_method')
        
        buyer = Buyer(
            user_id=current_user.id,
            shipping_address=shipping_address,
            payment_method=payment_method
        )
        db.session.add(buyer)
        db.session.commit()
        
        flash('You have also become a buyer, please login again')
        logout_user()  
        return redirect(url_for('auth.login'))  
    
    return render_template('auth/add_user_type_buyer.html', is_seller=is_seller)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user, form.remember_me.data)
            
            is_buyer = Buyer.query.filter_by(user_id=user.id).first() is not None
            is_seller = Seller.query.filter_by(user_id=user.id).first() is not None
            
            if is_buyer and is_seller:
                session['user_id'] = user.id
                return redirect(url_for('auth.choose_user_type'))
            elif is_seller:
                return redirect(url_for('orders.seller_orders'))
            
            return redirect(url_for('main.index'))
        flash('Invalid username or password.')
    return render_template('auth/login.html', form=form)


@auth.route('/login/choose-user-type', methods=['GET', 'POST'])
def choose_user_type():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('auth.login'))
    
    if request.method == 'POST':
        user_type = request.form.get('user_type')
        if user_type == 'buyer':
            return redirect(url_for('main.index'))
        elif user_type == 'seller':
            return redirect(url_for('products.seller_products'))
        else:
            flash('Invalid user type selected.')
    
    return render_template('auth/choose_user_type.html')


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('main.index'))