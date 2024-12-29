from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from models import User
from database import db

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password_hash, password):
            session['username'] = username
            session['privilege'] = user.privilege
            return redirect(url_for('home.home_page'))
        flash('Invalid username or password.')
        return redirect(url_for('auth.login'))
    return render_template('login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        privilege = request.form.get('admin', '0')  # Default to '0' if not provided
        if User.query.filter_by(username=username).first():
            flash('Username already exists.')
            return redirect(url_for('auth.register'))
        hashed_password = generate_password_hash(password, method='pbkdf2')
        new_user = User(username=username, password_hash=hashed_password, privilege=privilege)
        db.session.add(new_user)
        db.session.commit()
        flash('Account created successfully! You can now log in.')
        return redirect(url_for('auth.login'))
    return render_template('register.html')

@auth_bp.route('/logout', methods=['POST'])
def logout():
    session.pop('username', None)
    session.pop('privilege', None)  # Clear the privilege as well
    return redirect(url_for('auth.login'))

@auth_bp.route('/delete_account', methods=['GET', 'POST'])
def delete_account():
    if 'username' not in session:
        return redirect(url_for('auth.login'))  # Ensure the user is logged in

    user = User.query.filter_by(username=session['username']).first()
    if not user:
        return redirect(url_for('auth.login'))  # Handle case if user does not exist

    if request.method == 'POST':
        # Delete the user's account
        db.session.delete(user)
        db.session.commit()

        # Logout the user after deletion
        session.pop('username', None)
        session.pop('privilege', None)

        flash('Account deleted successfully.')
        return redirect(url_for('auth.login'))  # Redirect to login page after deletion

    return render_template('delete_account.html', username=user.username)
