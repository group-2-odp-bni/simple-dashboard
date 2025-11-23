from supabase import create_client
import os
from dotenv import load_dotenv
from datetime import datetime
import pandas as pd
load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def save_survey_response(data: dict):
    """Insert sebagai JSON ke kolom 'data'."""
    payload = {
        "timestamp": datetime.utcnow().isoformat(),
        "data": data 
    }

    try:
        supabase.table("survey_responses").insert(payload).execute()
        return True
    except Exception as e:
        print("Supabase insert failed:", e)
        return False
def fetch_all_responses():
    """Fetch all survey responses as a pandas DataFrame."""
    try:
        res = supabase.table("survey_responses").select("*").execute()
        rows = res.data or []

        if not rows:
            return pd.DataFrame()

        records = []
        for row in rows:
            entry = row["data"].copy()
            entry["timestamp"] = row["timestamp"]  # include timestamp from table
            records.append(entry)

        return pd.DataFrame(records)

    except Exception as e:
        print("Fetch error:", e)
        return pd.DataFrame()