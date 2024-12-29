from flask import Blueprint, render_template, request, redirect, url_for, session
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
        return 'Invalid username or password.'
    return render_template('login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        privilage = request.form['admin']
        if User.query.filter_by(username=username).first():
            return 'Username already exists.'
        hashed_password = generate_password_hash(password, method='pbkdf2')
        new_user = User(username=username, password_hash=hashed_password, privilege=privilage)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('auth.login'))
    return render_template('register.html')

@auth_bp.route('/logout', methods=['POST'])
def logout():
    print(request.method)  # This will print the method that was used for the request
    session.pop('username', None)
    return redirect(url_for('auth.login'))

@auth_bp.route('/delete_account', methods=['GET', 'POST'])
def delete_account():
    if 'username' not in session:
        return redirect(url_for('auth.login'))  # Ensure the user is logged in

    # Get the user to delete from the database
    user = User.query.filter_by(username=session['username']).first()

    if request.method == 'POST':
        # Delete the user's account
        db.session.delete(user)
        db.session.commit()

        # Logout the user after deletion
        session.pop('username', None)

        return redirect(url_for('auth.login'))  # Redirect to login page after deletion

    return render_template('delete_account.html', username=user.username)

