from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv

load_dotenv('backend/.env')
url = os.getenv('DATABASE_URL')
if not url:
    raise RuntimeError('DATABASE_URL not found')

engine = create_engine(url, pool_pre_ping=True, fast_executemany=True)

tables = [
    'feeding_records',
    'pet_weights',
    'emotion_records',
    'ai_chat_histories',
    'cat_profiles',
]

with engine.begin() as conn:
    before = {}
    after = {}
    deleted = {}

    for t in tables:
        before[t] = conn.execute(text(f"SELECT COUNT(1) FROM {t}")).scalar_one()

    for t in tables:
        conn.execute(text(f"DELETE FROM {t}"))

    for t in tables:
        after[t] = conn.execute(text(f"SELECT COUNT(1) FROM {t}")).scalar_one()
        deleted[t] = before[t] - after[t]

print('Cleared pet-related data tables (users preserved):')
for t in tables:
    print(f"- {t}: deleted {deleted[t]} rows (now {after[t]})")
