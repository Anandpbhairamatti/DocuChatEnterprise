import sys
import os
sys.path.append(r"C:\Users\Administrator\OneDrive\Desktop\CQA\backend")
from app.db.session import engine
from sqlalchemy import text

with engine.connect() as conn:
    conn.execute(text("UPDATE documents SET visibility = 'ORGANIZATION' WHERE visibility IS NULL"))
    conn.commit()
print("Updated visibilities successfully.")
