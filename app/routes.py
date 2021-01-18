from flask import current_app as app

# a simple page that says hello
@app.route("/")
def hello():
    return "Hello, World!"