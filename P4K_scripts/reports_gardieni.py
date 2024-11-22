import requests
import pandas as pd
from datetime import datetime, timedelta
import re



pontaje = '1055979739011096708'

#  date format YYYY-MM-DD \ winter time (-2h)  summer time(-3h)    : 00:00 for 24.10.2023 is 21:00 23.10.2023 (summer time)
start_date_str = '2024-06-15T19:00:00.000000+00:00'
start_date_frm = start_date_str[:10]


def auth_disc():
    headers = {
        'Authorization': 'MjM2MTM1MzAzMjQzNDk3NDc0.GckeC1.jlFGnfwZLXv38W5wu9ASxp3o4sxKR_r4qq33jY',
    }
    return headers


def snowflake_converter(time):
    start_date = datetime.strptime(time, '%Y-%m-%dT%H:%M:%S.%f%z')
    snowflake_time = int((start_date.timestamp() - 1420070400) * 1000) << 22
    return snowflake_time


def minute_pontaje(s):
    f_s = s.replace("**", "")
    match = re.search(r'\(\s*(\d+)\s*minute\)', f_s)
    if match:
        return match.group(1)
    else:
        pass


def discord_id(s):
    if isinstance(s, dict) and 'username' in s:
        return s['username']
    else:
        return ""


def req_pontaje(channel_id, start_date):
    
    headers = auth_disc()
    inv = []

    snowflake_time = snowflake_converter(start_date)
    response = requests.get(f'https://discord.com/api/v10/channels/{channel_id}/messages?after={snowflake_time}',
                            headers=headers)

    while response.status_code == 200:

        messages = response.json()
        if not messages:
            break  # No more messages to fetch

        for message in messages:
            inv.append(message)

        last_message_id = messages[0]['id']
        print(last_message_id)
        response = requests.get(f'https://discord.com/api/v10/channels/{channel_id}/messages?after={last_message_id}',
                                headers=headers)

    df = pd.DataFrame(inv)
    print(df.head(5))
    df.to_csv('diicot.csv')
  
    df = df[['content', 'author', 'edited_timestamp', 'timestamp', 'reactions', 'id']]

    start_date = datetime.fromisoformat(start_date)
    end_date = start_date + timedelta(days=7)

    df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
    df = df[(df['timestamp'] <= end_date)]
    df = df[(df['reactions'].isna())]
    df = df[(df['edited_timestamp'].isna())]
    
    return df


def calc_pontaj(start_date):

    df_pontaje = req_pontaje(pontaje, start_date)
    
    # Procesare Pontaje
   
    df_pontaje['discord_id'] = df_pontaje['author'].apply(discord_id)
    df_pontaje['minute_pontaj'] = df_pontaje['content'].apply(minute_pontaje)
    df_pontaje = df_pontaje.dropna(subset='minute_pontaj')
    df_pontaje['minute_pontaj'] = df_pontaje['minute_pontaj'].astype(int)
    
    total_pontaje = df_pontaje['minute_pontaj'].sum()
   
    df_pontaje = df_pontaje[(df_pontaje['minute_pontaj'] >= 15)]
    

    df_pontaje = df_pontaje.groupby('discord_id')['minute_pontaj'].sum()


    df_pontaje.to_csv(f"politie\penitenciar\pontaje_{start_date_frm}.csv")
    print(f"In aceasta saptamana Agentii A.N.P au efectuat {round(total_pontaje / 60, 1)} ore de munca in cadrul Penitenciarului")


calc_pontaj(start_date_str)
