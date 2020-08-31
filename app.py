# -*- coding: utf-8 -*-

import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin
from flask_dropzone import Dropzone
from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash

basedir = os.path.abspath(os.path.dirname(__file__))

db = SQLAlchemy()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
app.config['SECRET_KEY'] = b'mysupersecretkey'.hex()
app.config['UPLOADED_PATH'] = os.path.join(basedir, 'uploads')
app.config['DROPZONE_MAX_FILE_SIZE'] = 1024
app.config['DROPZONE_TIMEOUT'] = 5 * 60 * 1000
app.config['DROPZONE_ALLOWED_FILE_CUSTOM'] = True
app.config['DROPZONE_ALLOWED_FILE_TYPE'] = 'text/*, .fit, .tcx'

db.init_app(app)

dropzone = Dropzone(app)


login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.init_app(app)



auth = Blueprint('auth', __name__)

@auth.route('/login')
def login():
    return render_template('login.html')

@auth.route('/login', methods=['POST'])
def login_post():
    email = request.form.get('email')
    password = request.form.get('password')
    remember = True if request.form.get('remember') else False

    check_user = User.query.filter_by(email=email).first()

    # check if the user actually exists
    # take the user-supplied password, hash it, and compare it to the hashed password in the database
    if not check_user or not check_password_hash(check_user.password, password):
        flash('Please check your login details and try again.')
        return redirect(url_for('auth.login')) # if the user doesn't exist or password is wrong, reload the page

    # if the above check passes, then we know the user has the right credentials
    login_user(check_user, remember=remember)
    return redirect(url_for('main.profile'))

@auth.route('/signup')
def signup():
    return render_template('signup.html')

@auth.route('/signup', methods=['POST'])
def signup_post():
    email = request.form.get('email')
    name = request.form.get('name')
    password = request.form.get('password')

    user = User.query.filter_by(email=email).first() # if this returns a user, then the email already exists in database

    if user: # if a user is found, we want to redirect back to signup page so user can try again
        return redirect(url_for('auth.signup'))

    # create a new user with the form data. Hash the password so the plaintext version isn't saved.
    new_user = User(email=email, name=name, password=generate_password_hash(password, method='sha256'))

    # add the new user to the database
    db.session.add(new_user)
    db.session.commit()
    
    check_user = User.query.filter_by(email=email).first() # if this returns a user, then the email already exists in database

    if check_user: # if a user is found, we want to redirect back to signup page so user can try again
        return redirect(url_for('main.profile'))
    else:
        return "What the fuck"
    
@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))




class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True) # primary keys are required by SQLAlchemy
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(1000))


@login_manager.user_loader
def load_user(user_id):
    # since the user_id is just the primary key of our user table, use it in the query for the user
    return User.query.get(int(user_id))

app.register_blueprint(auth)
db.create_all(app=app) # pass the create_app result so Flask-SQLAlchemy gets the configuration.

main = Blueprint('main', __name__)

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/profile')
@login_required
def profile():
    return render_template('base_user.html', name=current_user.name)

@app.route("/upload", methods=['POST', 'GET'])
def upload():
    if request.method == 'POST':
        f = request.files.get('file')
        f.save(os.path.join(app.config['UPLOADED_PATH'], f.filename))
    return render_template('upload.html')



app.register_blueprint(main)
if __name__=='__main__':
    app.run()