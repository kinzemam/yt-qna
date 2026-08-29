from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from rag import answer_question

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class QuestionRequest(BaseModel):
    video_id: str
    question: str

@app.post("/ask")
def ask_question(request: QuestionRequest):
    response = answer_question(request.video_id, request.question)

    return {"answer": response}