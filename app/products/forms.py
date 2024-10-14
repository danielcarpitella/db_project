from flask_wtf import FlaskForm
from wtforms import StringField, DecimalField, IntegerField, SubmitField, SelectField
from wtforms.validators import DataRequired, Email, EqualTo
from wtforms import ValidationError
from app import db

from ..models import User  

class EditProductForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    description = StringField('Description', validators=[DataRequired()])
    brand = StringField('Brand', validators=[DataRequired()])
    price = DecimalField('Price', validators=[DataRequired()])
    quantity = IntegerField('Quantity', validators=[DataRequired()])
    submit = SubmitField('Update')