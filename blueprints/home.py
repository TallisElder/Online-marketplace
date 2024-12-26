from flask import Blueprint, render_template, session, redirect, url_for
from models import Listing
from database import db

home_bp = Blueprint('home', __name__)

@home_bp.route('/home')
def home_page():
    if not session.get('username'):
        return redirect(url_for('auth.login'))
    listings = Listing.query.all()
    return render_template('home.html', listings=listings)