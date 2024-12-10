from flask_wtf import FlaskForm
from wtforms import StringField, DecimalField, IntegerField, SubmitField, SelectField, TextAreaField
from wtforms.validators import DataRequired, Email, EqualTo, NumberRange
from wtforms import ValidationError
from app import db

class ReviewForm(FlaskForm):
    rate = IntegerField('Rate', validators=[DataRequired(), NumberRange(min=1, max=5, message="Il voto deve essere tra 1 e 5")])
    title = StringField('Title', validators=[DataRequired()])
    description = TextAreaField('Body', validators=[DataRequired()])
    submit = SubmitField('Submit')