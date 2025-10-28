"""
PGP Web Application - Flask App Factory
"""
import os
import logging
from flask import Flask
from flask_wtf.csrf import CSRFProtect

csrf = CSRFProtect()


def create_app(config_name=None):
    """Create and configure the Flask application."""
    app = Flask(__name__)

    # Configuration
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')

    from app.config import config
    app.config.from_object(config[config_name])

    # Set up logging
    setup_logging(app)

    # Initialize extensions
    csrf.init_app(app)

    # Register blueprints
    from app.main import bp as main_bp
    app.register_blueprint(main_bp)

    from app.api import bp as api_bp
    app.register_blueprint(api_bp, url_prefix='/api')

    # Create necessary directories
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['GNUPG_HOME'], exist_ok=True)

    app.logger.info(f"PGP Web Application started in {config_name} mode")
    app.logger.info(f"Upload folder: {app.config['UPLOAD_FOLDER']}")
    app.logger.info(f"GnuPG home: {app.config['GNUPG_HOME']}")

    return app


def setup_logging(app):
    """Configure logging for the application."""
    if not app.debug and not app.testing:
        # Production logging
        if not os.path.exists('logs'):
            os.mkdir('logs')

        file_handler = logging.FileHandler('logs/pgp_app.log')
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)

        app.logger.setLevel(logging.INFO)
        app.logger.info('PGP Web Application startup')
    else:
        # Development logging - more verbose
        logging.basicConfig(
            level=app.config.get('LOG_LEVEL', logging.DEBUG),
            format='%(asctime)s %(name)s %(levelname)s: %(message)s'
        )

        # Enable debug logging for our modules
        logging.getLogger('app').setLevel(logging.DEBUG)
        logging.getLogger('app.services').setLevel(logging.DEBUG)
        logging.getLogger('app.main').setLevel(logging.DEBUG)
        logging.getLogger('app.utils').setLevel(logging.DEBUG)
