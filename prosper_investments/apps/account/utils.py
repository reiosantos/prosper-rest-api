from datetime import date, datetime


def generate_account_number():
    user_id = date.strftime(datetime.now(), "%y%m%d%H%M")
    return user_id
