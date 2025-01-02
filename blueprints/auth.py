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

@auth_bp.route('/registerAdmin', methods=['GET', 'POST'])
def register_admin():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Check if the username already exists
        if User.query.filter_by(username=username).first():
            flash('Username already exists.')
            return redirect(url_for('auth.register_admin'))

        # Hash the password and set privilege level to '1' (Admin)
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256', salt_length=16)
        new_admin = User(username=username, password_hash=hashed_password, privilege=1)

        # Add the new admin user to the database
        db.session.add(new_admin)
        db.session.commit()

        flash('Admin account created successfully!')
        return redirect(url_for('admin.admin_panel'))  # Redirect to the admin panel

    return render_template('register_admin.html')

@auth_bp.route('/change_password', methods=['GET', 'POST'])
def change_password():
    if not session.get('username'):
        flash('You need to be logged in to change your password.')
        return redirect(url_for('auth.login'))

    if request.method == 'POST':
        current_password = request.form['current_password']
        new_password = request.form['new_password']
        confirm_password = request.form['confirm_password']

        # Fetch the user from the database
        user = User.query.filter_by(username=session['username']).first()

        if not user or not check_password_hash(user.password_hash, current_password):
            flash('Current password is incorrect.')
            return redirect(url_for('auth.change_password'))

        if new_password != confirm_password:
            flash('New passwords do not match.')
            return redirect(url_for('auth.change_password'))

        # Update the password and commit to the database
        user.password_hash = generate_password_hash(new_password, method='pbkdf2:sha256', salt_length=16)
        db.session.commit()

        flash('Password changed successfully. Please log in again.')
        session.clear()  # Log the user out
        return redirect(url_for('auth.login'))

    return render_template('change_password.html')
