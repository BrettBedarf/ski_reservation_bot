import datetime

from flask_wtf import FlaskForm
from wtforms import validators, PasswordField, DateField, StringField
from wtforms.fields.html5 import EmailField
from .forms_attribute_select import AttribSelectField

from package.providers import providers


def validate_date(form, field):
    if field.data and field.data < datetime.date.today():
        raise validators.ValidationError("The date cannot be in the past!")


class ReservationForm(FlaskForm):
    #  Options format tuple (value,label,{attributes})
    resort_options = [
        (resort["resort"], resort["resort"], {"data-provider": resort["provider"]})
        for resort in providers
    ]
    resort = AttribSelectField(
        "Resort",
        choices=resort_options,
        validators=[validators.InputRequired("No resort selected!")],
    )
    date = DateField(
        "Reservation Date",
        format="%m/%d/%Y",
        validators=[validators.InputRequired("No date selected!"), validate_date],
    )
    email = EmailField(
        "Provider Email", validators=[validators.InputRequired("No email provided!")]
    )
    password = PasswordField(
        "Provider Password",
        validators=[validators.InputRequired("No password provided!")],
    )
    # TODO validate phone is needed for provider
    phone = StringField(
        "Phone", validators=[validators.Length(9, 10, "Phone number must be 9 or 10 digits!")]
    )
