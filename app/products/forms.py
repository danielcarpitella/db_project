from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, DecimalField, IntegerField, SelectField, SubmitField
from wtforms.validators import DataRequired
from app.models import Category

class EditProductForm(FlaskForm):
    name = StringField('Nome', validators=[DataRequired()])
    description = TextAreaField('Descrizione', validators=[DataRequired()])
    category_id = SelectField('Categoria', coerce=int, validators=[DataRequired()])
    brand = StringField('Marca', validators=[DataRequired()])
    price = DecimalField('Prezzo', validators=[DataRequired()])
    quantity = IntegerField('Quantità', validators=[DataRequired()])
    submit = SubmitField('Salva')

    def __init__(self, *args, **kwargs):
        super(EditProductForm, self).__init__(*args, **kwargs)
        self.category_id.choices = [(category.id, category.title) for category in Category.query.all()]


class ReviewFilterForm(FlaskForm):
    star_rating = SelectField('Filter reviews', choices=[
        ('all', 'All'),
        ('1', '1 Star'),
        ('2', '2 Stars'),
        ('3', '3 Stars'),
        ('4', '4 Stars'),
        ('5', '5 Stars')
    ], default='all')
    submit = SubmitField('Filter')