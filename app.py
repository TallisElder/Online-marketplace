from flask import Flask
from database import db
from blueprints.auth import auth_bp
from blueprints.home import home_bp
from blueprints.account import account_bp
from blueprints.admin import admin_bp

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///marketplace.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
db.init_app(app)


# Register Blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(home_bp)
app.register_blueprint(account_bp)
app.register_blueprint(admin_bp)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Ensures database tables are created
    app.run(debug=True)
