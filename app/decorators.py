from functools import wraps
from flask import redirect, url_for, flash
from flask_login import current_user, login_required
from app.models import Seller, Buyer

def seller_required(f):
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        if not Seller.query.filter_by(user_id=current_user.id).first():  # se l'utente non è un seller torna alla home
            flash('You need to be a seller to access this page.', 'danger')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function

def buyer_required(f):
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        if not Buyer.query.filter_by(user_id=current_user.id).first():  # se l'utente non è un buyer torna alla home
            flash('You need to be a buyer to access this page.', 'danger')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function