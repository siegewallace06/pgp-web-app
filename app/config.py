"""
Configuration settings for the PGP Web Application
"""
import os
import logging
from datetime import timedelta

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    """Base configuration class."""
    SECRET_KEY = os.environ.get(
        'SECRET_KEY') or 'dev-secret-key-change-in-production'

    # File upload settings
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    UPLOAD_FOLDER = os.path.join(basedir, '..', 'uploads')
    ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'doc', 'docx', 'zip',
                          'gpg', 'asc', 'pgp', 'sig'}  # Added PGP-related extensions

    # GnuPG settings
    GNUPG_HOME = os.path.join(basedir, '..', 'gnupg_home')

    # Session settings
    PERMANENT_SESSION_LIFETIME = timedelta(hours=1)

    # Security settings
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = None


class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    TESTING = False

    # Enhanced logging for development
    LOG_LEVEL = logging.DEBUG


class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    TESTING = False

    # Production logging
    LOG_LEVEL = logging.INFO

    # Override with environment variables in production
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'fallback-secret-key'


class TestingConfig(Config):
    """Testing configuration."""
    DEBUG = True
    TESTING = True
    WTF_CSRF_ENABLED = False


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
