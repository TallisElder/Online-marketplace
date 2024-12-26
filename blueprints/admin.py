from flask import Blueprint, redirect, url_for, session
from models import Listing
from database import db

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/delete_listing/<int:listing_id>', methods=['POST'])
def delete_listing(listing_id):
    if not session.get('username'):
        return redirect(url_for('auth.login'))

    listing = Listing.query.get_or_404(listing_id)

    # Only allow the owner or admin to delete the listing
    if listing.username == session['username']:
        db.session.delete(listing)
        db.session.commit()
        return redirect(url_for('account.account'))

    return "Unauthorized action."