from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv

load_dotenv('backend/.env')
engine = create_engine(os.getenv('DATABASE_URL'), pool_pre_ping=True, fast_executemany=True)

tables = ['feeding_records','pet_weights','emotion_records','ai_chat_histories','cat_profiles','users']
with engine.begin() as conn:
    for t in tables:
        n = conn.execute(text(f"SELECT COUNT(1) FROM {t}")).scalar_one()
        print(f"{t}: {n}")
