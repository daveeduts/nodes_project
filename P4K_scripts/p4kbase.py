import pandas as pd
from datetime import datetime


def auth_disc():
    headers = {
        'Authorization': 'MjM2MTM1MzAzMjQzNDk3NDc0.GckeC1.jlFGnfwZLXv38W5wu9ASxp3o4sxKR_r4qq33jY',
    }
    return headers


def snowflake_converter(time):
    start_date = datetime.strptime(time, '%Y-%m-%dT%H:%M:%S.%f%z')
    snowflake_time = int((start_date.timestamp() - 1420070400) * 1000) << 22
    return snowflake_time

