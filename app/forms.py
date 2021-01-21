from wtforms import Form, validators, StringField, PasswordField, DateField
from wtforms.fields.html5 import EmailField
from .forms_attribute_select import AttribSelectField
from package.providers import providers


class ReservationForm(Form):
    #  Options format tuple (value,label,{attributes})
    resort_options = [
        (resort["resort"], resort["resort"], {"data-provider": resort["provider"]})
        for resort in providers
    ]
    resort = AttribSelectField(
        "Resort", resort_options, validators=[validators.InputRequired("No resort selected!")]
    )
    date = DateField("Reservation Date")
    email = EmailField("Provider Email")
    password = PasswordField("Provider Password")
