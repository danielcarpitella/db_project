from flask import Blueprint
from ..models import Product, Category, User, Order, Review

api = Blueprint('api', __name__)

from .import views

