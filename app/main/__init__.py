"""
Main blueprint for the PGP Web Application
"""
from flask import Blueprint

bp = Blueprint('main', __name__)
from app.main import routes
