import bcrypt
from db import get_conn
import os
import jwt
from datetime import datetime, timedelta,timezone

def create_token(user_id):
    payload = {
        "sub": str(user_id),
        "exp": datetime.now(timezone.utc) + timedelta(hours=24),
    }
    return jwt.encode(payload, os.environ["SECRET_KEY"], algorithm="HS256")

def decode_token(token):
    try:
        payload = jwt.decode(token, os.environ["SECRET_KEY"], algorithms=["HS256"])
        return int(payload["sub"])
    except (jwt.PyJWTError, KeyError, ValueError):
        return None

def create_user(email, password):
    hashed = bcrypt.hashpw(password.encode(),bcrypt.gensalt()).decode()
    with get_conn() as conn:
        row = conn.execute("INSERT INTO users (email, password_hash) values (%s, %s) returning id", (email, hashed)).fetchone()
    return row[0]

def verify_user(email, password):
    with get_conn() as conn:
        row = conn.execute("select id, password_hash from users where email = %s", (email,)).fetchone()
    if row is None:
        return None
    user_id, hash = row
    if bcrypt.checkpw(password.encode(), hash.encode()):
        return user_id
    return None

def user_exists(email):
    with get_conn() as conn:
        rows = conn.execute("select id from users where email = %s", (email,)).fetchone()
    if rows is None:
        return False
    return True
if __name__=="__main__":
    # print("Created user id: ", create_user("test_example.com", "mypassword123") )
    print(verify_user("test_example.com", "mypassword123"))
        
        