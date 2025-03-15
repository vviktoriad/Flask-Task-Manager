from flask import Flask, Blueprint, render_template, redirect, url_for, flash, session
from flask_login import LoginManager, login_user, login_required, logout_user
from forms import LoginForm, RegisterForm
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User


auth = Blueprint('auth', __name__)

login_manager = LoginManager() #implementuje moduł logowania 
login_manager.login_view = 'auth.login'


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and check_password_hash(user.password_hash, form.password.data):
            login_user(user, remember=form.remember.data)
            if form.remember.data:
                session['username'] = form.username.data
                session['password'] = form.password.data
            else:
                session.pop('username', None)
                session.pop('password', None)
            return redirect(url_for('tasks.add_task'))
        flash('Invalid username or password', 'danger')
    else:
        form.username.data = session.get('username', '')
        form.password.data = session.get('password', '')
    return render_template('login.html', form=form)

@auth.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        if User.query.filter_by(username=form.username.data).first():
            flash('This username is already taken!', 'danger')
            return redirect(url_for('auth.register'))
        if form.password.data != form.confirm_password.data:
            flash('Passwords do not match!', 'danger')
            return redirect(url_for('auth.register'))
        hashed_password = generate_password_hash(form.password.data, method='pbkdf2')
        new_user = User(username=form.username.data, password_hash=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('auth.login'))
    return render_template('register.html', form=form)

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

