import pandas as pd
from p4kbase import auth_disc, snowflake_converter
import requests
from datetime import datetime, timedelta
import re

chest_logs = "1078003865301032990"

# Date format YYYY-MM-DD \ winter time (-2h) summer time(-3h) : 00:00 for 24.10.2023 is 21:00 23.10.2023 (summer time)
# start_date_str = '2024-07-14T13:00:00.000000+00:00'
# start_date_frm = start_date_str[:10]

pret_obiecte = {'Acid Lysergic': 5000,
                'AK47': 3000,
                'Amethyst': 1000000,
                'Amphetamina': 50000,
                'Aur': 100000,
                'Bani Murdari': 0.5,
                'Bronz': 40000,
                'Cannabis Sativa': 5000,
                'Card de credit': 50000,
                'Ceas Antic': 10000,
                'Ceas vechi de aur': 10000,
                'Cocaina': 100000,
                'Cocaina Alkaloid': 10000,
                'Conocybe Filiaris': 500000,
                'Craniu Auriu': 40000,
                'DMT': 100000,
                'Esenta de trabuc': 500000,
                'Fier': 35000,
                'Frunze Coca': 9000,
                'Heroina': 120000,
                'Iarba': 50000,
                'Ketamina': 800000,
                'Lingou Cayo': 250000,
                'LSD': 50000,
                'M4A1': 2500,
                'Mini C4': 500000,
                'Moneda Sindicat': 2500000,
                'NEGEV': 2500,
                'Otel': 10000,
                'Pachet de Tigari BT': 200000,
                'PCP': 50000,
                'PCP Neprocesat': 5000,
                'Platina': 250000,
                'Stick USB(full)': 10000,
                'Sulf': 10000,
                'Tigara BT': 20000,
                'Trabuc': 1000000,
                'Ulei THC': 60000,
                'Subutex': 100000,
                'Metadona': 500000,
                'GHB': 300000,
                'Morfina': 400000,
                'Carlig': 350000
                }


def evidence_req(channel_id, start_date):
    headers = auth_disc()
    inv = []

    snowflake_time = snowflake_converter(start_date)
    response = requests.get(f'https://discord.com/api/v10/channels/{channel_id}/messages?after={snowflake_time}',
                            headers=headers)

    while response.status_code == 200:
        messages = response.json()
        if not messages:
            break

        for message in messages:
            inv.append(message)

        last_message_id = messages[0]['id']
        response = requests.get(f'https://discord.com/api/v10/channels/{channel_id}/messages?after={last_message_id}',
                                headers=headers)

    df = pd.DataFrame(inv)
    df = df[['content', 'timestamp', 'id']]

    start_date = datetime.fromisoformat(start_date)

    if len(df) > 0:
        df = df[['content', 'timestamp']]
        return df

    return None


def unique_id(s):
    result = re.search(r'\((\d+)\)', s)
    if result:
        return result.group(1)


def faction(s):
    result = re.search(r'faction_chest\|(.+?)\|', s)
    if result:
        return result.group(1)
    return None


def quantity(s):
    result = re.search(r',\s(\d+)x', s)
    if result:
        return result.group(1)
    return None


def object(s):
    result = re.search(r'\d+x\s(.+?)\.', s)
    if result:
        return result.group(1)
    return None


def exclude_rows(df, column, substring):
    return df[~df[column].str.contains(substring, na=False)]


def data_builder_exchange(start_date):

    start_date_frm = start_date[:10]
    
    df = evidence_req(chest_logs, start_date)
    df = exclude_rows(df, 'content', 'a retras')

    df['CNP'] = df['content'].apply(unique_id)
    df['Factiune'] = df['content'].apply(faction)
    df['Obiect'] = df['content'].apply(object)
    df['Cantitate'] = df['content'].apply(quantity).astype('int')
    
    df = df[['Factiune', 'CNP', 'Obiect', 'Cantitate']]
    df = df.groupby(['CNP', 'Obiect', 'Factiune']).sum().reset_index()

    #df.to_csv("raw.csv")

    df['Pret'] = df['Obiect'].map(pret_obiecte)
    df = df.dropna(subset=['Pret'])
    
    df['suma'] = df['Cantitate'] * df['Pret']

    df_pret = df[['Factiune', 'CNP', 'suma']]
    df_pret = df_pret.groupby(['Factiune', 'CNP']).sum().reset_index()

    df_pret.to_csv(fr"P4K_scripts\exchange\exchange_{start_date_frm}.csv")
    print(f"Exchange {start_date_frm} done!")

    return df_pret


# data_builder_exchange(start_date_str)
