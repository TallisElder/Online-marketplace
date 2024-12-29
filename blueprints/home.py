import os
from flask import Blueprint, render_template, request, session, redirect, url_for, flash
from werkzeug.utils import secure_filename
from models import Listing  # Assuming a model file is used
from database import db  # Assuming a database setup

home_bp = Blueprint('home', __name__)

UPLOAD_FOLDER = 'static/listingPhotos'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# Ensure the upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Helper function to validate file extensions
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@home_bp.route('/home')
def home_page():
    if not session.get('username'):
        return redirect(url_for('auth.login'))
    listings = Listing.query.all()

    is_admin = session.get('privilege') == '1'

    return render_template('home.html', listings=listings)

@home_bp.route('/create_listing', methods=['POST'])
def create_listing():
    if not session.get('username'):
        return redirect(url_for('auth.login'))

    name = request.form['name']
    description = request.form['description']
    price = request.form['price']
    file = request.files['image']

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)

        # Add the new listing to the database
        new_listing = Listing(
            name=name,
            description=description,
            price=float(price),
            image_url=filepath,
            username=session['username']  # Store the creator's username
        )
        db.session.add(new_listing)
        db.session.commit()
        flash('Listing created successfully!')
        return redirect(url_for('home.home_page'))
    else:
        flash('Invalid file type. Please upload a valid image.')
        return redirect(url_for('home.home_page'))
    
@home_bp.route('/delete_listing/<int:listing_id>', methods=['POST'])
def delete_listing(listing_id):
    if not session.get('username'):
        return redirect(url_for('auth.login'))

    # Query the listing
    listing = Listing.query.get_or_404(listing_id)

    # Check if the user is the owner of the listing or has admin privilege (privilege=1)
    if session['username'] != listing.username and session.get('privilege') != 1:  # Check privilege 1 for admin
        flash('You do not have permission to delete this listing.')
        return redirect(url_for('home.home_page'))

    # Get the file path of the image
    image_filepath = listing.image_url  # Assuming image_url is stored with the full path like 'static/ListingPhotos/filename.jpg'
    
    # Delete the file from the filesystem
    if os.path.exists(image_filepath):
        os.remove(image_filepath)
    
    # Delete the listing from the database
    db.session.delete(listing)
    db.session.commit()

    flash('Listing and associated image deleted successfully.')
    return redirect(url_for('home.home_page'))
