import pandas as pd
import os
from datetime import datetime

CSV_FILE = "survey_results.csv"

def save_survey_response(data: dict) -> bool:
    """
    Menyimpan data survei ke file CSV lokal.
    Jika file belum ada, akan dibuat baru.
    Jika sudah ada, data akan ditambahkan (append).
    """
    try:
        data['timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        df_new = pd.DataFrame([data])
        
        if not os.path.exists(CSV_FILE):
            df_new.to_csv(CSV_FILE, index=False)
        else:
            df_new.to_csv(CSV_FILE, mode='a', header=False, index=False)
            
        return True
    except Exception as e:
        print(f"Error saving to CSV: {e}")
        return False

def fetch_all_responses() -> pd.DataFrame:
    """Membaca semua data dari file CSV lokal."""
    try:
        if os.path.exists(CSV_FILE):
            return pd.read_csv(CSV_FILE)
        else:
            return pd.DataFrame() # Kembalikan tabel kosong jika file belum ada
    except Exception as e:
        print(f"Error reading CSV: {e}")
        return pd.DataFrame()