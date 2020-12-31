from calendar import monthrange

month_names = ["January", "February", "March", "April", "May", "June", "July",
               "August", "September", "October", "November", "December"]


def validate_date(day, month, year):
    # make sure the date exists
    if day > monthrange(year, month)[1]:
        return False
