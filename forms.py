# -*- coding: utf-8 -*-

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextField
from wtforms.validators import DataRequired, Email

class UsernamePasswordForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    
class EmailForm(FlaskForm):
    email = TextField("Email", validators=[DataRequired(), Email()])
    
class PasswordForm(FlaskForm):
    password = TextField("Password", validators=[DataRequired()])
    