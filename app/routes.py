from flask import current_app as app
from flask import render_template

# a simple page that says hello
@app.route("/")
@app.route("/index")
def index():
    return render_template("index.html")
