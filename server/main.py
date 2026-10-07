from fastapi import FastAPI, Depends
from fastapi.security import HTTPBearer,HTTPAuthorizationCredentials
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from rag import answer_question
import psycopg
from auth import create_user, verify_user, user_exists, create_token,decode_token
from fastapi import HTTPException
from db import get_conn
from chats import create_chat, add_message, get_chat_owner, list_chats, get_messages
from typing import Optional
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
bearer = HTTPBearer()
class Credentials(BaseModel):
    email: str
    password: str
@app.post("/signup")
def signup(creds: Credentials):
    try:
        user_id = create_user(creds.email, creds.password)
    except psycopg.errors.UniqueViolation:
        raise HTTPException(400, detail="Email already registered")
    return {"id": user_id, "email":creds.email}

@app.post("/login")
def login(creds: Credentials):
    try:
        if not user_exists(creds.email):
            raise HTTPException(401, detail = "user not found")
        user = verify_user(creds.email, creds.password)
        if user is None:
            raise HTTPException(401, detail = "Invalid email or password")
        return {"access_token": create_token(user)}
    except psycopg.errors.OperationalError:
        raise HTTPException(500, detail = "Database unavailable")    

def get_current_user(creds: HTTPAuthorizationCredentials = Depends(bearer)):
    user_id = decode_token(creds.credentials)
    if user_id is None:
        raise HTTPException(401, detail="Invalid or expired token")
    return user_id

@app.get("/me")
def me(user_id: int = Depends(get_current_user)):
    with get_conn() as conn:
        row = conn.execute("select id, email from users where id = %s", (user_id,)).fetchone()
    if row is None:
        raise HTTPException(401, detail="user not found")
    return {"id", row[0], "email", row[1]}

class QuestionRequest(BaseModel):
    video_id: str
    question: str

class AskRequest(BaseModel):
    video_id: str
    question: str
    chat_id: Optional[int] = None

@app.post("/ask")
def ask_question(req: AskRequest, user_id: int = Depends(get_current_user)):
    chat_id = req.chat_id
    if chat_id is None:
        chat_id = create_chat(user_id, req.video_id)
    elif get_chat_owner(chat_id) != user_id:
        raise HTTPException(404, detail="Chat not found")
    add_message(chat_id, "user", req.question)
    history = get_messages(chat_id)
    answer = answer_question(req.video_id, req.question, history)
    add_message(chat_id, "ai", answer)
    return {"chat_id": chat_id, "answer": answer}

@app.get("/chats")
def my_chats(user_id: int = Depends(get_current_user)):
    return list_chats(user_id)

@app.get("/chats/{chat_id}/messages")
def chat_messages(chat_id: int, user_id: int = Depends(get_current_user)):
    if(get_chat_owner(chat_id) != user_id):
        raise HTTPException(404, detail="chat not found")
    return get_messages(chat_id)