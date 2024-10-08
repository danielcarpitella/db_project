import os
import sys
import click
from flask import Flask, render_template, redirect, url_for, flash
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo
from werkzeug.security import generate_password_hash
from flask_migrate import Migrate, upgrade
from flask_login import LoginManager

from app import create_app, db
from app.models import User   

app = create_app()
migrate = Migrate(app, db)   

@app.shell_context_processor
def make_shell_context():
    return dict(app=app, db=db, User=User)


if __name__ == '__main__':
    app.run(debug=True)