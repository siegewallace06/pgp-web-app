"""
WSGI entry point for the PGP Web Application
"""
from app import create_app
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import the app after loading environment variables

# Create the application instance
application = create_app()

# For compatibility with different WSGI servers
app = application

if __name__ == "__main__":
    application.run(
        host='0.0.0.0',
        port=int(os.environ.get('PORT', 5000)),
        debug=os.environ.get('FLASK_ENV') == 'development'
    )
