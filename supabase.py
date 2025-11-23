import os
import json
from datetime import datetime
import pandas as pd
from sqlalchemy import create_engine, text

CSV_FILE = "survey_results.csv"
DATABASE_URL = os.getenv("DATABASE_URL")

_engine = None

if DATABASE_URL:
    try:
        _engine = create_engine(DATABASE_URL, pool_pre_ping=True, connect_args={"sslmode": "require"})
        with _engine.begin() as conn:
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS survey_responses (
                    id SERIAL PRIMARY KEY,
                    timestamp TIMESTAMPTZ NOT NULL,
                    data_json JSONB NOT NULL
                );
            """))
        print("DB Connected.")
    except Exception as e:
        print(f"Database init failed: {e}")
        _engine = None


def save_survey_response(data: dict) -> bool:
    """Simpan survey ke DB, fallback CSV kalau gagal."""
    data['timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if _engine:
        try:
            with _engine.begin() as conn:
                conn.execute(
                    text("INSERT INTO survey_responses (timestamp, data_json) VALUES (:timestamp, :json)"),
                    {"timestamp": data["timestamp"], "json": json.dumps(data, ensure_ascii=False)}
                )
            return True
        except Exception as e:
            print(f"DB error, fallback to CSV: {e}")

    try:
        df_new = pd.DataFrame([data])
        if not os.path.exists(CSV_FILE):
            df_new.to_csv(CSV_FILE, index=False)
        else:
            df_new.to_csv(CSV_FILE, mode="a", index=False, header=False)
        return True
    except Exception as e:
        print(f" CSV Error: {e}")
        return False


def fetch_all_responses():
    """Ambil semua data (DB prioritas, CSV fallback)."""
    if _engine:
        try:
            with _engine.begin() as conn:
                rows = conn.execute(text("SELECT data_json FROM survey_responses")).fetchall()
            return pd.json_normalize([r[0] for r in rows])
        except Exception as e:
            print(f"DB read failed: {e}")

    if os.path.exists(CSV_FILE):
        return pd.read_csv(CSV_FILE)

    return pd.DataFrame()
