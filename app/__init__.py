from flask import Flask
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_jwt_extended import JWTManager
from flask_bcrypt import Bcrypt


bootstrap = Bootstrap()
db = SQLAlchemy()
migrate = Migrate()

bcrypt = Bcrypt()
jwt = JWTManager()

login_manager = LoginManager()
login_manager.login_view = 'auth.login'

def create_app():
    app = Flask(__name__)
    
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql+psycopg2://postgres:postgres@localhost:5432/basi_DB'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  
    app.config['SECRET_KEY'] = 'chiaveSuperSegreta'
    
    bootstrap.init_app(app)
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)
    jwt.init_app(app)
    
    
    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/auth')
    
    from .api import api as api_blueprint  
    app.register_blueprint(api_blueprint, url_prefix='/api') 
    
    from app.products import products as products_blueprint
    app.register_blueprint(products_blueprint)
    
    from app.cart import cart as cart_blueprint
    app.register_blueprint(cart_blueprint)
    
    from app.orders import orders as orders_blueprint
    app.register_blueprint(orders_blueprint)

    return app
