"""
API blueprint for AJAX operations
"""
from app.api import routes
from flask import Blueprint

bp = Blueprint('api', __name__)
