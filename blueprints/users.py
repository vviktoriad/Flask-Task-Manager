from flask import Flask, Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from models import db, User
from admin import role_required

users = Blueprint('users', __name__)

@users.route('/users')
@login_required
@role_required('admin')
def list_users():
    users_list = User.query.all()
    return render_template('users.html', users=users_list, tasks=current_user.tasks)

@users.route('/delete_user/<int:id>', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def delete_user(id):
    user = User.query.get(id)
    for task in user.tasks:
        db.session.delete(task)
    db.session.delete(user)
    db.session.commit()
    flash('User deleted successfully!', 'success')
    return redirect(url_for('users.list_users'))

@users.route('/promote_user/<int:id>', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def promote_user(id):
    user = User.query.get(id)
    user.role = 'admin'
    db.session.commit()
    flash('User role changed to admin!', 'success')
    return redirect(url_for('users.list_users'))

@users.route('/demote_user/<int:id>', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def demote_user(id):
    user = User.query.get(id)
    user.role = 'user'
    db.session.commit()
    flash('User role changed to user!', 'success')
    return redirect(url_for('users.list_users'))

@users.route('/user_tasks>', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def user_tasks():
    users = User.query.all()
    render_template('users.html', users=users, tasks=current_user.tasks)