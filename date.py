from datetime import datetime, timedelta

def str_to_date(str, format="%Y-%m-%d"):
    # convert str to date:
    if type(str) == datetime:
        str = datetime.strftime(str, format)
    return datetime.strptime(str[ : 10], format)

def add_day(date, day):
    return date + timedelta(days = day)

def is_open(str_date):
    # return True if the passed date parameter is in the future, othervise return False
    close_at = add_day(str_to_date(str_date), 1)
    return close_at > datetime.now()

def today(format = '%Y-%m-%d'):
    # return today's date
    return datetime.today().strftime(format)