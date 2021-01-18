import os
from flask import Flask


def create_app(test_config=None):
    # Factory creates and configures flask app
    app = Flask(__name__, instance_relative_config=True)
    #  TODO Initialize config and plugins

    #  Define context
    with app.app_context():
        # Include routes
        from . import routes

    return app
