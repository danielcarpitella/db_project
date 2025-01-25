from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.products import products
from ..models import Product, Category, Review, Seller
from app import db
from .forms import EditProductForm
from functools import wraps


@products.route('/products')
def all_products():
    search = request.args.get('search', '', type=str)
    category_id = request.args.get('category', None, type=int)
    selected_brand = request.args.get('brand', '', type=str)
    min_price = request.args.get('min_price', None, type=float)
    max_price = request.args.get('max_price', None, type=float)
    page = request.args.get('page', 1, type=int)
    per_page = 5

    products_query = Product.query.order_by(Product.created_at.desc())

    if search:
        products_query = products_query.filter(Product.name.ilike(f'%{search}%'))

    if category_id:
        products_query = products_query.filter(Product.category_id == category_id)
    
    if selected_brand:
        products_query = products_query.filter(Product.brand.ilike(f'%{selected_brand}%'))
    
    if min_price is not None:
        products_query = products_query.filter(Product.price >= min_price)
    
    if max_price is not None:
        products_query = products_query.filter(Product.price <= max_price)
        
    pagination = products_query.paginate(page=page, per_page=per_page, error_out=False)
    products = pagination.items
    categories = Category.query.all()
    brands = db.session.query(Product.brand).distinct().all()
    brands = [brand[0] for brand in brands]

    return render_template('products.html', products=products, categories=categories, brands=brands, pagination=pagination, search=search, category_id=category_id, selected_brand=selected_brand, min_price=min_price, max_price=max_price)

# seba

@products.route('/product/<int:product_id>')
def single_product(product_id):
    product = Product.query.get_or_404(product_id)
    reviews = Review.query.filter_by(product_id=product_id).order_by(Review.created_at.desc()).all()
    return render_template('single_product.html', product=product, reviews=reviews)


# seba ha fatto da qua in giù per quanto riguarda seller-products


def seller_required(f):
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        if not Seller.query.filter_by(user_id=current_user.id).first(): # se l'utente non è un seller torna alla home
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function



@products.route('/seller/products')
@seller_required
def seller_products():
    products = Product.query.filter_by(user_id=current_user.id).order_by(Product.created_at.desc()).all()
    return render_template('seller_products.html', products=products)


@products.route('/seller/products/edit-product/<int:product_id>', methods=['GET', 'POST'])
@seller_required
def seller_edit_product(product_id):
    product = Product.query.get_or_404(product_id)
    form = EditProductForm(obj=product)

    if form.validate_on_submit():
        product.name=form.name.data
        product.description=form.description.data
        product.brand=form.brand.data
        product.price=form.price.data
        product.quantity=form.quantity.data
        product.category_id=form.category_id.data

        db.session.commit()

        return redirect(url_for('products.seller_products'))

    return render_template('edit_product.html', product=product, form=form)


@products.route('/seller/products/delete-product/<int:product_id>', methods=['POST'])
@seller_required
def seller_delete_product(product_id):
    product = Product.query.get_or_404(product_id)

    db.session.delete(product)
    db.session.commit()

    return redirect(url_for('products.seller_products'))


@products.route('/seller/products/add-product', methods=['GET', 'POST'])
@seller_required
def seller_add_product():
    form = EditProductForm()

    if form.validate_on_submit():
        product = Product (
            user_id=current_user.id,
            category_id=form.category_id.data,  # SIA QUA SIA SU EDIT DEVO METTERE IL MENU A TENDINA CON IL TESTO E L'IF PER L'ID
            name=form.name.data,
            description=form.description.data,
            brand=form.brand.data,
            price=form.price.data,
            quantity=form.quantity.data
        )
        db.session.add(product)
        db.session.commit()

        return redirect(url_for('products.seller_products'))

    return render_template('add_product.html', form=form)
