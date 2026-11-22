
# Import the Flask application factory.
from run import create_app

# Import the shared database instance.
from extensions import db

# Import all models so SQLAlchemy knows about their tables.
from models import (
    BookType,
    Category,
    ContactMessage,
    Favorite,
    Loan,
    Resource,
    Review,
    User
)


# Create our Flask application.
app = create_app()


# Work within the Flask application context.
with app.app_context():

    # Create tables that do not already exist.
    db.create_all()

    # Display confirmation.
    print("E-Library database tables created successfully!")
