import requests
import pandas as pd
import re
from datetime import datetime, timedelta
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import time
from p4kbase import auth_disc, snowflake_converter


amenzi = '950694548881940562'
jails = '953701937822437416'

#  date format YYYY-MM-DD \ winter time (-2h)  summer time(-3h)    : 00:00 for 24.10.2023 is 21:00 23.10.2023 (summer time)

start_date_str = '2024-06-15T19:00:00.000000+00:00'
start_date_frm = start_date_str[:10]


def unique_id(s):
    result = re.search(r'\((\d+)\)', s)
    if result:
        return result.group(1)
    else:
        return None


def badge_number(s):
    result = re.search(r'\[(\d+)\]', s)
    if result:
        return result.group(1)
    else:
        return None


def fines_req(channel_id, start_date):
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
    df = df[['content', 'timestamp', 'id']]

    start_date = datetime.fromisoformat(start_date)
    end_date = start_date + timedelta(days=7)

    df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
    df = df[(df['timestamp'] <= end_date)]

    df = df.drop_duplicates(keep='first')
    #df.to_csv("fines_raw_now.csv")

    return df


def jail_req(channel_id, start_date):
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
    df = df[['content', 'timestamp', 'id']]

    start_date = datetime.fromisoformat(start_date)
    end_date = start_date + timedelta(days=7)

    df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
    df = df[(df['timestamp'] <= end_date)]

    df = df.drop_duplicates(keep='first')
    #df.to_csv("jails_raw.csv")

    return df


def extract_id_fines(s):
    split_text = s.split("politistul")[1].split("pentru")[0].strip()
    return split_text


def extract_id_jails(s):
    match = re.search(r'(Politistul|Jucatorul)\s(.*?)\s(l-a)', s)
    if match:
        split_text = match.group(2)
        return split_text


def sum_of_fine(s):
    match = re.search(r'de (\d[\d,.]*)\$', s)
    if match:
        return match.group(1).replace(',', '').replace('.', '')


def type_of_fine(d):
    if d < 500000:
        return "AV"
    else:
        return "AMENDA"


def citizen_id(s):
    match = re.search(r'Jucatorul [^\(]*\((\d+)\)[^\(]* a', s)
    if match:
        return match.group(1)


def fraud_detection(df):

    df['timestamp'] = pd.to_datetime(df['timestamp'], utc=True)
    df = df.sort_values(by='timestamp')
    merged_df = pd.merge(df, df, on='cnp_civil', how='inner', suffixes=('_first', '_second'))

    # Randuri unde cetateanul a primit amenda de la politisti diferiti in mai putin de 5 minute
    potential_fraud = merged_df[
        (merged_df['cnp_agent_first'] != merged_df['cnp_agent_second']) &
        (abs(merged_df['timestamp_first'] - merged_df['timestamp_second']) <= pd.Timedelta(minutes=5))
        ]

    potential_fraud = potential_fraud.drop_duplicates(subset=['cnp_civil', 'timestamp_first', 'timestamp_second'])
    potential_fraud.to_csv(fr'politie\frauda_rapoarte\rapoarte_duble_{start_date_frm}.csv', index=False)


def data_builder(start_date):
    df_fines = fines_req(amenzi, start_date)
    df_jails = jail_req(jails, start_date)

    # Procesare Rapoarte

    df_fines['agent'] = df_fines['content'].apply(extract_id_fines)
    df_fines['cnp_agent'] = df_fines['agent'].apply(unique_id)
    df_fines['insigna'] = df_fines['agent'].apply(badge_number)
    df_fines['valoare_amenda'] = df_fines['content'].apply(sum_of_fine)
    df_fines['valoare_amenda'] = pd.to_numeric(df_fines['valoare_amenda'])
    df_fines['tip_amenda'] = df_fines['valoare_amenda'].apply(type_of_fine)

    # Calcul Rapoarte AMENZI
    df_amenzi = df_fines[(df_fines["tip_amenda"] == "AMENDA")]
    total_amenzi = df_amenzi['valoare_amenda'].sum()
    nr_amenzi = len(df_amenzi)
    cnp_count_a = df_amenzi['cnp_agent'].value_counts()
    df_amenzi = df_amenzi.copy()
    df_amenzi.loc[:, 'n_amenzi'] = df_amenzi['cnp_agent'].map(cnp_count_a)
    df_amenzi['n_amenzi'] = df_amenzi['n_amenzi'].fillna(0)
    df_amenzi = df_amenzi.drop_duplicates(subset='cnp_agent', keep='first')

    df_amenzi = df_amenzi[['agent', 'insigna', 'cnp_agent', 'n_amenzi']]

    # Calcul Rapoarte AV total
    df_av_t = df_fines[(df_fines["tip_amenda"] == "AV")]
    nr_av_scris = len(df_av_t)
    cnp_count_av = df_av_t['cnp_agent'].value_counts()
    df_av_t = df_av_t.copy()
    df_av_t.loc[:, 'n_av_total'] = df_av_t['cnp_agent'].map(cnp_count_av).fillna(0)
    df_av_t = df_av_t.drop_duplicates(subset='cnp_agent', keep='first')
    df_av_t = df_av_t[['cnp_agent', 'n_av_total']]

    print(f'Saptamana trecuta Politia Romana a emis {nr_amenzi} amenzi in valoare totala de: {total_amenzi} RON si un numar de {nr_av_scris} avertismente scrise')

    # Calcul Rapoarte AV-uri valide
    df_av = df_fines[(df_fines["tip_amenda"] == "AV")]
    df_av = df_av.copy()
    df_av.loc[:, 'cnp_civil'] = df_av['content'].apply(citizen_id)
    df_av = df_av[['timestamp', 'cnp_civil', 'cnp_agent']]
    df_av['timestamp'] = pd.to_datetime(df_av['timestamp'], utc=True)
    df_av = df_av.sort_values(by='timestamp')
    df_av['last_timestamp'] = df_av.groupby(['cnp_agent', 'cnp_civil'])['timestamp'].shift()
    df_av['time_diff'] = df_av['timestamp'] - df_av['last_timestamp']
    av_valide = df_av[df_av['time_diff'].isnull() | (df_av['time_diff'] > pd.Timedelta(hours=6))]
    df_av = av_valide.groupby('cnp_agent').size().reset_index(name='n_av')

    fraud_detection(av_valide)
    #df_av.to_csv("av_raw.csv")

    # Procesare Inchisoare
    df_jails['agent'] = df_jails['content'].apply(extract_id_jails)
    df_jails['cnp_agent'] = df_jails['agent'].apply(unique_id)
    df_jails['insigna'] = df_jails['agent'].apply(badge_number)

    cnp_count_j = df_jails['cnp_agent'].value_counts()
    df_jails['n_jail'] = df_jails['cnp_agent'].map(cnp_count_j)
    df_jails['n_jail'] = df_jails['n_jail'].fillna(0).copy()

    df_jails = df_jails.drop_duplicates(subset='cnp_agent', keep='first')
    df_jails = df_jails[['agent', 'insigna', 'cnp_agent', 'n_jail']]

    return df_av_t, df_av, df_amenzi, df_jails


def report_maker(start_date):

    av_tot, av, fines, jails = data_builder(start_date)

    all_agents = pd.concat([fines, jails]).copy()
    all_agents.drop_duplicates(subset='cnp_agent', inplace=True)
    all_agents = all_agents[['agent', 'insigna', 'cnp_agent']]

    left_join = pd.merge(fines, jails, on='cnp_agent', how='left')
    right_join = pd.merge(fines, jails, on='cnp_agent', how='right')

    final_report = pd.concat([left_join, right_join], ignore_index=True).drop_duplicates()

    final_report = all_agents.merge(final_report, how='left', on='cnp_agent')
    final_report = pd.merge(final_report, av_tot, on='cnp_agent', how='left')
    final_report = pd.merge(final_report, av, on='cnp_agent', how='left')
    final_report = final_report[['agent', 'insigna', 'cnp_agent', 'n_av_total', 'n_av', 'n_amenzi', 'n_jail']]

    final_report['n_amenzi'] = final_report['n_amenzi'].fillna(0)
    final_report['n_jail'] = final_report['n_jail'].fillna(0)
    final_report['n_av'] = final_report['n_av'].fillna(0)
    final_report['n_av_total'] = final_report['n_av_total'].fillna(0)
    final_report['total_rapoarte'] = final_report['n_amenzi'] + final_report['n_jail'] + final_report['n_av']

    final_report.to_csv(fr'politie\rapoarte\rapoarte_{start_date_frm}.csv')

    return final_report


def google_updater(df, cnp_column_idx, rap_idx):

    
    SERVICE_ACCOUNT_FILE = fr''   #aici pui fisierul .json de la google script
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]

    creds = ServiceAccountCredentials.from_json_keyfile_name(SERVICE_ACCOUNT_FILE, scope)
    client = gspread.authorize(creds)

    # Open the Google Sheet
    spreadsheet = client.open('DEPARTAMENTUL POLITIE PRO4KINGS')  #numele google sheets
    sheet = spreadsheet.worksheet('TEST_SCRIPT')  #numele filei

    sheet_data = sheet.get_all_values()
    sheet_df = pd.DataFrame(sheet_data[1:], columns=sheet_data[0])

    for index, row in df.iterrows():

        cnp_value = row['cnp_agent']
        
        matching_row_index = sheet_df[sheet_df.iloc[:, cnp_column_idx - 1] == cnp_value].index
        if not matching_row_index.empty:

            sheet_row_index = matching_row_index[0] + 2
            sheet.update_cell(sheet_row_index, rap_idx, row['total_rapoarte'])

        time.sleep(2)

    print("Docs Updated")


def main(week):

    df = report_maker(start_date_str)
     
    cnp_column_idx = 2     
    rap_idx = 17      

    if week == 2:
        rap_idx = rap_idx + 1

    elif week == 3:
        rap_idx = rap_idx + 2  

    elif week == 4:
        rap_idx = rap_idx + 3 

    #google_updater(df, cnp_column_idx, rap_idx)


main(week=1)
