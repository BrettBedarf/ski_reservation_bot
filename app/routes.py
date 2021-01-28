from flask import current_app as app
from flask import render_template, request
from flask.templating import render_template_string

from app.forms import ReservationForm

# a simple page that says hello
@app.route("/", methods=["GET", "POST"])
@app.route("/index")
def index():
    form = ReservationForm()
    if form.validate_on_submit():
        return render_template_string("Success!")
    return render_template("reservation.html", form=form)
