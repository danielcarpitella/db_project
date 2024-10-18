from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, DecimalField, IntegerField, SelectField, SubmitField
from wtforms.validators import DataRequired, Length, Email, EqualTo, NumberRange
from ..models import User, Category
from wtforms import ValidationError


class ProductForm(FlaskForm):
    name = StringField('Nome', validators=[DataRequired(), Length(min=1, max=100)])
    description = TextAreaField('Descrizione', validators=[Length(max=500)])
    brand = StringField('Marca', validators=[Length(max=50)])
    price = DecimalField('Prezzo', validators=[DataRequired(), NumberRange(min=0)])
    quantity = IntegerField('Quantità', validators=[DataRequired(), NumberRange(min=0)])
    category_id = SelectField('Categoria', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Salva')

    def __init__(self, *args, **kwargs):
        super(ProductForm, self).__init__(*args, **kwargs)
        self.category_id.choices = [(category.id, category.title) for category in Category.query.all()]
        

class EditProfileForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired(), Length(min=1, max=50)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(min=1, max=50)])
    email = StringField('Email', validators=[DataRequired(), Email(), Length(min=1, max=100)])
    phone = StringField('Phone Number', validators=[DataRequired(), Length(min=1, max=20)])
    shipping_address = StringField('Shipping Address', validators=[DataRequired(), Length(min=1, max=200)])
    payment_method = SelectField('Payment Method', choices=[('Card', 'Card'), ('Paypal', 'Paypal'), ('Klarna', 'Klarna')], validators=[DataRequired()])
    submit = SubmitField('Save changes')


class EditSellerProfileForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired(), Length(min=1, max=50)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(min=1, max=50)])
    email = StringField('Email', validators=[DataRequired(), Email(), Length(min=1, max=100)])
    phone = StringField('Phone Number', validators=[DataRequired(), Length(min=1, max=20)])
    store_name = StringField('Store Name', validators=[DataRequired(), Length(min=1, max=100)])
    submit = SubmitField('Save changes')