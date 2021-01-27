import os
from flask import Flask

from .flask_config import FlaskConfig


def create_app(test_config=None):
    # Factory creates and configures flask app
    app = Flask(__name__, instance_relative_config=True)
    #  TODO Initialize config and plugins
    app.config.from_object(FlaskConfig)
    #  Define context
    with app.app_context():
        # Include routes
        from . import routes

    return app
