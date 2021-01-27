import os


class FlaskConfig(object):
    SECRET_KEY = os.environ.get("SECRET_KEY") or "use-env-in-production"
