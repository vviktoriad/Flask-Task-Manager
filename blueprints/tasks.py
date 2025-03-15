from flask import Flask, Blueprint, render_template, redirect, url_for, flash, request
from models import db, Task
from forms import TaskForm
from flask_login import login_required, current_user
from datetime import datetime


tasks = Blueprint('tasks', __name__)
@tasks.route('/')
@login_required
def index():
    return redirect(url_for('tasks.add_task'))

@tasks.route('/add_task', methods=['GET', 'POST'])
@login_required
def add_task():
    form = TaskForm()
    if form.validate_on_submit():
        new_task = Task(title=form.title.data, description=form.description.data, deadline=form.deadline.data, user_id=current_user.id)
        db.session.add(new_task)
        db.session.commit()
        flash('Task added successfully!', 'success')
        return redirect(url_for('tasks.add_task'))
    return render_template('tasks.html', form=form, tasks=current_user.tasks, header_text='Add Task')

@tasks.route('/edit_task/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_task(id):
    task = Task.query.get(id)
    form = TaskForm()

    if request.method == 'GET':
        form.submit.label.text = 'Edit Task'
        form.title.data = task.title
        form.description.data = task.description
        form.deadline.data = datetime.strptime(task.deadline, '%Y-%m-%d')

    if form.validate_on_submit():
        task.title = form.title.data
        task.description = form.description.data
        task.deadline = form.deadline.data
        db.session.commit()
        flash('Task edited successfully!', 'success')
        return redirect(url_for('tasks.add_task'))
    return render_template('tasks.html', form=form, tasks=current_user.tasks, header_text='Edit Task')

@tasks.route('/delete_task/<int:id>', methods=['GET', 'POST'])
@login_required
def delete_task(id):
    task = Task.query.get(id)
    db.session.delete(task)
    db.session.commit()
    form = TaskForm()
    flash('Task deleted successfully!', 'success')
    return render_template('tasks.html', form=form, tasks=current_user.tasks)



