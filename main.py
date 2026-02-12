from pyairtable import Api
from dotenv import load_dotenv
import streamlit as st
import pandas as pd
import os

load_dotenv()

API_TOKEN = os.getenv("API_TOKEN")
BASE_ID = os.getenv("BASE_ID")
TABLE_NAME = os.getenv("TABLE_NAME")

print(TABLE_NAME) 

api = Api(API_TOKEN)

table = api.table(BASE_ID, TABLE_NAME)

records = table.all()

print(f"Connexion OK, {len(records)} records trouvés")

st.set_page_config(page_title="Connect to Airtable", layout="wide")

