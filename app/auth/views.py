from flask import render_template, request, redirect, url_for, flash
from app import db
from .. models import User
from .forms import RegistrationForm, LoginForm
from . import auth
from werkzeug.security import generate_password_hash
from flask_login import login_user, logout_user, login_required, current_user

@auth.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            email=form.email.data,
            phone=form.phone.data,
            address=form.address.data,
            password = form.password.data
        )
        db.session.add(user)
        db.session.commit()
        flash('You can now log in.')
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html', form=form)
    
    
@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user, form.remember_me.data)
            return redirect(url_for('main.index'))
        flash('Invalid username or password.')
    return render_template('auth/login.html', form=form)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('main.index'))