import datetime
import random
import sys
import faker

from sqlalchemy.orm import load_only
from sqlalchemy.sql import ClauseElement
from app import create_app, db
from app.models import User, Buyer, Seller, Category, Product, Order, Review, Cart, ProductOrderQuantity, ProductsCart, SellerOrder


fake = faker.Faker()


def delete_all_data(session):
    session.query(ProductsCart).delete()
    session.query(ProductOrderQuantity).delete()
    session.query(Review).delete()
    session.query(Order).delete()
    session.query(Cart).delete()
    session.query(Product).delete()
    session.query(Category).delete()
    session.query(Seller).delete()
    session.query(Buyer).delete()
    session.query(User).delete()
    session.commit()
    print('all data deleted')


'''
Used to search for an object in the db with certain 
parameters and if it doesn't find it it creates it
'''
def get_or_create(session, model, defaults=None, **kwargs):
    instance = session.query(model).filter_by(**kwargs).first()
    if instance:
        return instance, False
    else:
        params = dict((k, v) for k, v in kwargs.items() if not isinstance(v, ClauseElement))
        params.update(defaults or {})
        instance = model(**params)
        db.session.add(instance)
        return instance, True


def create_fake_users(session, num_users=10):
    for _ in range(num_users):
        user_data = {
            'first_name': fake.first_name(),
            'last_name': fake.last_name(),
            'email': fake.unique.email(),
            'phone': fake.phone_number(),
            'address': fake.address(),
            'password': 'password'  
        }
        user, created = get_or_create(session, User, **user_data)
        if created:
            print(f'Created user: {user.email}')
    session.commit()


def create_fake_buyers(session, num_buyers=10):
    users = session.query(User).all()
    payment_methods = ['Card', 'Paypal', 'Klarna'] 
    
    for user in users[:num_buyers]:
        buyer_data = {
            'user_id': user.id,
            'shipping_address': fake.address(),
            'payment_method': random.choice(payment_methods)
        }
        buyer, created = get_or_create(session, Buyer, **buyer_data)
        if created:
            print(f'Created buyer for user: {user.email}')
    session.commit()


def create_fake_sellers(session, num_sellers=5):
    users = session.query(User).all()
    for user in users[:num_sellers]:
        seller_data = {
            'user_id': user.id,
            'store_name': fake.company()
        }
        seller, created = get_or_create(session, Seller, **seller_data)
        if created:
            print(f'Created seller for user: {user.email}')
    session.commit()
    

def create_fake_categories(session, num_categories=5):
    for _ in range(num_categories):
        category_data = {
            'title': fake.word(),
            'description': fake.catch_phrase()
        }
        category, created = get_or_create(session, Category, **category_data)
        if created:
            print(f'Created category: {category.title}')
    session.commit()


def create_fake_products(session, num_products=20):
    sellers = session.query(Seller).all()
    categories = session.query(Category).all()
    for _ in range(num_products):
        product_data = {
            'user_id': random.choice(sellers).user_id,
            'category_id': random.choice(categories).id,
            'name': fake.catch_phrase(), 
            'description': fake.text(),
            'brand': fake.company(),
            'price': round(random.uniform(10.0, 100.0), 2),
            'quantity': random.randint(1, 100)
        }
        product, created = get_or_create(session, Product, **product_data)
        if created:
            print(f'Created product: {product.name}')
    session.commit()


def create_fake_carts(session):
    buyers = session.query(Buyer).all()
    for buyer in buyers:
        cart_data = {
            'user_id': buyer.user_id
        }
        cart, created = get_or_create(session, Cart, **cart_data)
        if created:
            print(f'Created cart for buyer: {buyer.user_id}')
    session.commit()
    
def create_fake_products_cart(session):
    carts = session.query(Cart).all()
    products = session.query(Product).all()
    
    for cart in carts:
        num_products_in_cart = random.randint(1, 6)  # Numero casuale di prodotti per ogni carrello
        products_in_cart = random.sample(products, num_products_in_cart)  # Seleziona prodotti casuali per il carrello
        
        for product in products_in_cart:
            entry_data = {
                'product_id': product.id,
                'cart_id': cart.id,
                'quantity': random.randint(1, 5)
            }
            entry, created = get_or_create(session, ProductsCart, **entry_data)
            if created:
                print(f'Created product cart entry: {entry.product_id}, {entry.cart_id}')
    
    session.commit()


def create_fake_orders(session):
    buyers_with_cart = session.query(Buyer).join(Cart).all()
    
    for buyer in buyers_with_cart:
        cart = session.query(Cart).filter_by(user_id=buyer.user_id).first()
        if not cart or not cart.products:
            continue
        
        total_amount = sum(product_cart.product.price * product_cart.quantity for product_cart in cart.products)
        
        order_data = {
            'user_id': buyer.user_id,
            'total': total_amount,
            'shipping_address': buyer.shipping_address,
            'payment_method': buyer.payment_method
        }
        with session.no_autoflush:
            order, created = get_or_create(session, Order, **order_data)
            if created:
                print(f'Created order for buyer: {buyer.user_id} with total: {total_amount}')
                
                # Ensure the order is added to the session and committed
                session.add(order)
                session.flush()  # Ensure the order ID is generated
                
                # Create ProductOrderQuantity entries for each product in the cart
                for product_cart in cart.products:
                    entry_data = {
                        'product_id': product_cart.product_id,
                        'order_id': order.id,
                        'quantity': product_cart.quantity
                    }
                    entry, created = get_or_create(session, ProductOrderQuantity, **entry_data)
                    if created:
                        print(f'Created product order quantity entry: {entry.product_id}, {entry.order_id}')
                
                # Clear the cart after creating the order
                for product_cart in cart.products:
                    session.delete(product_cart)
                session.delete(cart)
    
    session.commit()
    

def create_fake_reviews(session, num_reviews=30):
    buyers = session.query(Buyer).all()
    products = session.query(Product).all()
    for _ in range(num_reviews):
        review_data = {
            'user_id': random.choice(buyers).user_id,
            'product_id': random.choice(products).id,
            'rate': random.randint(1, 5),
            'title': fake.sentence(),
            'description': fake.text()
        }
        review, created = get_or_create(session, Review, **review_data)
        if created:
            print(f'Created review: {review.title}')
    session.commit()  
 
 
def get_sellers_involved_in_order(session, order):
   
    #query for all products associated with the given order
    product_quantities = session.query(ProductOrderQuantity).filter_by(order_id=order.id).all()
    
    #for each product I retrieve the associated seller
    sellers = set()
    for pq in product_quantities:
        product = session.query(Product).filter_by(id=pq.product_id).first()
        if product:
            seller = session.query(Seller).filter_by(user_id=product.user_id).first()
            if seller:
                sellers.add(seller)
    
    sellers_list = list(sellers)   
    return sellers_list


def create_fake_sellers_orders(session):
    orders = session.query(Order).all()
    
    for order in orders:
        involved_sellers = get_sellers_involved_in_order(session, order)
        
        for seller in involved_sellers:
            entry_data = {
                'seller_id': seller.user_id,
                'buyer_order_id': order.id,
                'order_status': 'Pending',
            }
            entry, created = get_or_create(session, SellerOrder, **entry_data)
            if created:
                print(f'Created seller order entry: {entry.order_id}, {entry.seller_id}, {entry.buyer_order_id}')
    
    session.commit()
        

if __name__ == '__main__':
    app = create_app() 
    with app.app_context(): 
        delete_all_data(db.session)
        create_fake_users(db.session)
        create_fake_buyers(db.session)
        create_fake_sellers(db.session)
        create_fake_categories(db.session)
        create_fake_products(db.session)
        create_fake_carts(db.session)
        create_fake_products_cart(db.session)
        create_fake_orders(db.session)
        create_fake_sellers_orders(db.session)
        create_fake_reviews(db.session)
        print('Database seeded successfully')
        
  
    
            
