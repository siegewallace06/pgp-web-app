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

    # Add error handlers
    setup_error_handlers(app)

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


def setup_error_handlers(app):
    """Set up error handlers for the application."""
    from flask import jsonify, request
    from flask_wtf.csrf import CSRFError

    @app.errorhandler(CSRFError)
    def handle_csrf_error(e):
        app.logger.error(f"CSRF error: {e.description}")
        app.logger.error(f"Request URL: {request.url}")
        app.logger.error(f"Request method: {request.method}")
        app.logger.error(f"Request headers: {dict(request.headers)}")

        # Return JSON for API endpoints, HTML for regular pages
        if request.path.startswith('/api/') or request.path in ['/upload-file', '/encrypt-file', '/decrypt-file']:
            return jsonify({
                'success': False,
                'message': 'CSRF token missing or invalid. Please refresh the page and try again.',
                'error_type': 'csrf_error'
            }), 400
        else:
            return f"""
            <!DOCTYPE html>
            <html>
            <head><title>CSRF Error</title></head>
            <body>
                <h1>Security Error</h1>
                <p>CSRF token missing or invalid. Please refresh the page and try again.</p>
                <a href="javascript:history.back()">Go Back</a>
            </body>
            </html>
            """, 400

    @app.errorhandler(400)
    def handle_bad_request(e):
        app.logger.error(f"Bad request: {e}")
        app.logger.error(f"Request URL: {request.url}")
        app.logger.error(f"Request method: {request.method}")

        if request.path.startswith('/api/') or request.path in ['/upload-file', '/encrypt-file', '/decrypt-file']:
            return jsonify({
                'success': False,
                'message': 'Bad request',
                'error_type': 'bad_request'
            }), 400
        return str(e), 400

    @app.errorhandler(500)
    def handle_internal_error(e):
        app.logger.error(f"Internal server error: {e}")
        app.logger.error(f"Request URL: {request.url}")
        app.logger.error(f"Request method: {request.method}")

        if request.path.startswith('/api/') or request.path in ['/upload-file', '/encrypt-file', '/decrypt-file']:
            return jsonify({
                'success': False,
                'message': 'Internal server error',
                'error_type': 'server_error'
            }), 500
        return str(e), 500
        logging.getLogger('app.utils').setLevel(logging.DEBUG)
