import os
import psycopg
from dotenv import load_dotenv
load_dotenv()

def get_conn():
    return psycopg.connect(os.environ["DATABASE_URL"])

if __name__=="__main__":
    with get_conn() as conn:
        rows = conn.execute("select * from users").fetchall()
        print("connected. users: ", rows)