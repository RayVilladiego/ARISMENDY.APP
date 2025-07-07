import gspread
import pandas as pd
from google.oauth2.service_account import Credentials

# Cambia este valor por tu propio ID de Google Sheet
SHEET_ID = "TU_SPREADSHEET_ID"

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
SERVICE_ACCOUNT_FILE = "service_account.json"

def get_client():
    creds = Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE,
        scopes=SCOPES
    )
    return gspread.authorize(creds)

def load_contenedores():
    client = get_client()
    sheet = client.open_by_key(SHEET_ID)
    ws = sheet.worksheet("contenedores")
    data = ws.get_all_records()
    return pd.DataFrame(data)

def save_contenedores(df):
    client = get_client()
    sheet = client.open_by_key(SHEET_ID)
    ws = sheet.worksheet("contenedores")
    ws.clear()
    ws.update([df.columns.values.tolist()] + df.values.tolist())

def load_movimientos():
    client = get_client()
    sheet = client.open_by_key(SHEET_ID)
    ws = sheet.worksheet("movimientos")
    data = ws.get_all_records()
    return pd.DataFrame(data)

def save_movimientos(df):
    client = get_client()
    sheet = client.open_by_key(SHEET_ID)
    ws = sheet.worksheet("movimientos")
    ws.clear()
    ws.update([df.columns.values.tolist()] + df.values.tolist())
