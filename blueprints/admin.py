from flask import Blueprint, render_template, session, redirect, url_for, flash
from models import User  # Assuming a User model exists
from database import db

admin_bp = Blueprint('admin', __name__)

# Admin panel to view and delete users
@admin_bp.route('/admin')
def admin_panel():
    if not session.get('username') or session.get('privilege') != 1:
        flash("You must be logged in as an admin to access this page.")
        return redirect(url_for('auth.login'))

    # Fetch all users from the database (excluding the current admin user)
    users = User.query.filter(User.username != session['username']).all()

    return render_template('admin.html', users=users)

# Route to delete a user account
@admin_bp.route('/delete_user/<int:user_id>', methods=['POST'])
def delete_user(user_id):
    if not session.get('username') or session.get('privilege') != 1:
        flash("You must be logged in as an admin to perform this action.")
        return redirect(url_for('auth.login'))

    user = User.query.get_or_404(user_id)

    # Deleting the user from the database
    db.session.delete(user)
    db.session.commit()

    flash(f"User {user.username} deleted successfully.")
    return redirect(url_for('admin.admin_panel'))
