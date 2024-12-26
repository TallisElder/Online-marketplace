from flask import Blueprint, render_template, session, redirect, request, url_for
from werkzeug.security import generate_password_hash
from models import Listing, User
from database import db

account_bp = Blueprint('account', __name__)

@account_bp.route('/account', methods=['GET', 'POST'])
def account():
    if not session.get('username'):
        return redirect(url_for('auth.login'))

    user_listings = Listing.query.filter_by(username=session['username']).all()

    if request.method == 'POST':
        new_password = request.form['new_password']
        confirm_password = request.form['confirm_password']

        if new_password != confirm_password:
            return "Passwords do not match."

        user = User.query.filter_by(username=session['username']).first()
        user.password_hash = generate_password_hash(new_password, method='sha256')
        db.session.commit()
        return "Password updated successfully."

    return render_template('account.html', user_listings=user_listings)