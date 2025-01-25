from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.reviews import reviews
from ..models import Product, Category, Review, ProductOrderQuantity, Order, SellerOrder
from .forms import ReviewForm
from app import db
from functools import wraps


@reviews.route('/product/<int:product_id>/review', methods=['GET', 'POST'])
@login_required
def product_review(product_id):
    # se l'utente non ha acquistato il prodotto non può scrivere la recensione, bisognerebbe dare un messaggio di errore
    # sulla tabella sellers_orders deve essere che order_status=delivered, se non lo è allora redirecta
    if not (
        SellerOrder.query
        .join(Order, SellerOrder.buyer_order_id == Order.id)
        .join(ProductOrderQuantity, ProductOrderQuantity.order_id == Order.id)
        .filter(
            ProductOrderQuantity.product_id == product_id,
            Order.user_id == current_user.id,
            # SellerOrder.order_status == 'Delivered'  # se commentato: sufficiente che sia stato acquistato; se non commentato: deve essere consegnato
        )
        .first()
    ):
        flash("Non puoi lasciare una recensione di un prodotto che non hai acquistato", "danger")
        return redirect(url_for('products.single_product', product_id=product_id))

    user_review = Review.query.filter_by(product_id=product_id, user_id=current_user.id).first()
    form = ReviewForm(obj=user_review)

    if form.validate_on_submit():
        if not Review.query.filter_by(product_id=product_id, user_id=current_user.id).first():
            review = Review (
                user_id = current_user.id,
                product_id = product_id,
                rate = form.rate.data,
                title = form.title.data,
                description = form.description.data
            )
            db.session.add(review)
        else:
            user_review.rate = form.rate.data
            user_review.title = form.title.data
            user_review.description = form.description.data
        db.session.commit()
        return redirect(url_for('products.single_product', product_id=product_id))

    return render_template('your_review.html', form=form)
