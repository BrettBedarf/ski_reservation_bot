from flask import current_app as app
from flask import render_template

from app.forms import ReservationForm

# a simple page that says hello
@app.route("/")
@app.route("/index")
def index():
    form = ReservationForm()
    return render_template("reservation.html", form=form)
