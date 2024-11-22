import requests
import pandas as pd
import re
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import time
from datetime import datetime, timedelta
from p4kbase import auth_disc, snowflake_converter
from reports_exchange import data_builder_exchange


diicot = '981877373756669952'
categorie_evidente = '1199450883113623585'
categorie_rapoarte = '1154018840913661973'

#  date format YYYY-MM-DD \ winter time (-2h)  summer time(-3h)    : 00:00 for 24.10.2023 is 21:00 23.10.2023 (summer time)

start_date_str = '2024-08-25T13:00:00.000000+00:00'
start_date_frm = start_date_str[:10]
google_sheet_name = 'Superiori_DIS'
worksheet_name = 'Evidenta'


def discord_cnp(s):
    match = re.search(r'\d+', s)
    if match:
        return match.group()


def status_suspect(s):
    match = re.search(r'status suspect:\s*([a-zA-Z])\s*', s, re.IGNORECASE)
    if match:
        return match.group(1)


def req_canale(server_id, category_id_rapoarte, category_id_evidente):
    
    headers = auth_disc()

    response = requests.get(f'https://discord.com/api/v10/guilds/{server_id}/channels', headers=headers)

    if response.status_code == 200:
        channels = response.json()
       
        channels_rapoarte = [channel for channel in channels if channel['parent_id'] == category_id_rapoarte]
       
        channel_id_rapoarte = [channel['id'] for channel in channels_rapoarte]
        channel_names_rapoarte = [channel['name'] for channel in channels_rapoarte]
        df_info_rapoarte = pd.DataFrame(zip(channel_id_rapoarte, channel_names_rapoarte), columns=['chan_id_r', 'chan_name_r'])
        df_info_rapoarte['cnp'] = df_info_rapoarte['chan_name_r'].apply(discord_cnp)

        channels_evidente = [channel for channel in channels if channel['parent_id'] ==  category_id_evidente]

        channel_id_evidente = [channel['id'] for channel in channels_evidente]
        channel_names_evidente = [channel['name'] for channel in channels_evidente]
        df_info_evidente = pd.DataFrame(zip(channel_id_evidente, channel_names_evidente), columns=['chan_id_e', 'chan_name_e'])
        df_info_evidente['cnp'] = df_info_evidente['chan_name_e'].apply(discord_cnp)

        channels_info = pd.merge(df_info_rapoarte,df_info_evidente, how='left', on='cnp')
        channels_info = channels_info[['cnp', 'chan_name_r', 'chan_id_r', 'chan_id_e']]

        return channels_info
    
    else: print("Error from channels requests")


def req_rapoarte(start_date, channel):
    
    headers = auth_disc()
    
    snowflake_time = snowflake_converter(start_date)

    inv = []
    last_message_id = None

    response = requests.get(f'https://discord.com/api/v10/channels/{channel}/messages?after={snowflake_time}',
                            headers=headers)

    while response.status_code == 200:

        messages = response.json()
        if not messages:
            break 

        for message in messages:
            inv.append(message)

        last_message_id = messages[0]['id']
        response = requests.get(f'https://discord.com/api/v10/channels/{channel}/messages?after={last_message_id}',
                                headers=headers)

    df = pd.DataFrame(inv)

    if len(df) > 0:
        df = df[['content', 'author', 'timestamp']]
        return df
    
    return None


def data_builder_rapoarte(start_date, server_id, category_id_rapoarte, category_id_evidente):

    inv_nume, inv_r_M, inv_r_V, inv_e, inv_cnp= [], [], [], [], []
    df = req_canale(server_id, category_id_rapoarte, category_id_evidente)
    df_exchange = data_builder_exchange(start_date_str)

    # Procesare Rapoarte
    for index, row in df.iterrows():
        nume = row['chan_name_r']
        chan_id_r = row['chan_id_r']
        chan_id_e = row['chan_id_e']
        cnp = row['cnp']

        print(f"Rapoarte: {nume}")

        # Fetch rapoarte + categorizare dupa tip
        rapoarte_chan_id_r = req_rapoarte(start_date, chan_id_r)
        
        if rapoarte_chan_id_r is not None:
            
            rapoarte_chan_id_r['status_suspect'] = rapoarte_chan_id_r['content'].apply(status_suspect).str.upper() 

            #rapoarte_chan_id_r.to_csv(f'rezultae_{row['chan_name_r']}.csv')
            
            rapoarte_chan_id_r.loc[rapoarte_chan_id_r['status_suspect'] == "", 'status_suspect'] = pd.NA
            rapoarte_chan_id_r = rapoarte_chan_id_r.dropna(subset=['status_suspect'])

            count_r = rapoarte_chan_id_r['status_suspect'].value_counts()
            
            inv_nume.append(nume)
            inv_r_M.append(count_r.get('M', 0)) 
            inv_r_V.append(count_r.get('V', 0))  
            inv_cnp.append(cnp)
        
        else:
            inv_nume.append(nume)
            inv_r_M.append(0)
            inv_r_V.append(0)
            inv_cnp.append(cnp) 

        
        # Fetch evidente
        rapoarte_chan_id_e = req_rapoarte(start_date, chan_id_e)
        
        try:
            rapoarte_chan_id_e = rapoarte_chan_id_e[rapoarte_chan_id_e['content'].str.contains('NUME')]
            count_e = len(rapoarte_chan_id_e)
            
            if count_e < 1: 
                print(f"{nume} nu are evidente")
        except: 
                count_e = 0
                print(f"{nume} nu are evidente")

        inv_e.append(count_e)
      

    evidenta = {
        'cnp': inv_cnp,
        'agent': inv_nume,
        'rap_m': inv_r_M,
        'rap_v': inv_r_V,
        'rap_e': inv_e,
    }
    
    df_evidenta = pd.DataFrame(evidenta)
    
    df_final = pd.merge(df_evidenta, df_exchange, how='left', left_on='cnp', right_on='CNP')
    df_final = df_final[['cnp', 'agent', 'rap_m', 'rap_v', 'rap_e','suma']]
    df_final['suma'] = df_final['suma'].fillna("0$")

    df_final = mesaj_discord(df_final)

    return df_final


def mesaj_discord(df):
    
    inv_mesaj = []

    for index, row in df.iterrows():
        
        cnp = row['cnp']
        nume = row['agent']
        rap_v = row['rap_v']
        rap_m = row['rap_m']
        rap_e = row['rap_e']
        exchange = row['suma']
        norma = "0 $"
        
        if rap_v >= 10 and rap_m >= 5 and rap_e >= 5: 
            norma = "30.000.000 $"

        mesaj = f"""
**Felicitari {nume} pentru activitatea facuta saptamana aceasta !
Nr.Suspecti capturati in viata: {rap_v}
Nr.Suspecti decedati : {rap_m}
Nr. Evidente: {rap_e}
Nr. Teste efectuate: 

Sanctiuni Actuale: 
Responsabilitate: 

Suma exchange: {exchange}
Bonus Norma:  {norma}
Numar Rapoarte Total: {rap_m + rap_v + rap_e}

Salariu Total: **\n"""

        inv_mesaj.append(mesaj)

    df['mesaj'] = inv_mesaj

    return df


def google_updater(df, cnp_column_idx, rap_m_idx, rap_v_idx, rap_ev_idx, exchange_col_idx):

    
    SERVICE_ACCOUNT_FILE = fr'P4K_scripts\DIICOT\diicot-35bf0f5f431a.json'
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]

    creds = ServiceAccountCredentials.from_json_keyfile_name(SERVICE_ACCOUNT_FILE, scope)
    client = gspread.authorize(creds)

    # Open the Google Sheet
    
    sheet = client.open(google_sheet_name).worksheet(worksheet_name)  
    sheet_data = sheet.get_all_values()
    sheet_df = pd.DataFrame(sheet_data[1:], columns=sheet_data[0])

    for index, row in df.iterrows():

        cnp_value = row['cnp']
        
        matching_row_index = sheet_df[sheet_df.iloc[:, cnp_column_idx - 1] == cnp_value].index
        if not matching_row_index.empty:

            sheet_row_index = matching_row_index[0] + 2
            sheet.update_cell(sheet_row_index, rap_m_idx, row['rap_m'])
            sheet.update_cell(sheet_row_index, rap_v_idx, row['rap_v'])
            sheet.update_cell(sheet_row_index, rap_ev_idx, row['rap_e'])
            sheet.update_cell(sheet_row_index,exchange_col_idx, row['suma'])
        
        time.sleep(5)

    print("Docs Updated")


def sheets_idx():
    
    cnp_column_idx = 2     
    rap_m_idx = 7  
    rap_v_idx = 8  
    rap_ev_idx = 9
    exchange_col_idx = 10        

    return cnp_column_idx, rap_m_idx, rap_v_idx, rap_ev_idx, exchange_col_idx
   
    
def main():
    
    df = data_builder_rapoarte(start_date_str, diicot, categorie_rapoarte, categorie_evidente)
    df.to_csv(fr"P4K_scripts\DIICOT\rapoarte\rapoarte_{start_date_frm}.csv", index=False)
    
    df_mesaj = df[['agent', 'mesaj']]
    df_mesaj.to_csv(fr"P4K_scripts\DIICOT\rapoarte_msj\mesaj_rapoarte_{start_date_frm}.csv", index=False) 
    
    cnp_column_idx, rap_m_idx, rap_v_idx, rap_ev_idx, exchange_col_idx = sheets_idx()
    google_updater(df, cnp_column_idx, rap_m_idx, rap_v_idx, rap_ev_idx, exchange_col_idx)


if __name__ == "__main__":
    main()
