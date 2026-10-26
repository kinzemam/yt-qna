# YouTube Q&A (RAG)

Ask questions about any YouTube video and get answers grounded in its transcript, with timestamps that point to the relevant moments. Users sign up, log in, and keep their own saved conversations.

**Live demo:** https://yt-qna.vercel.app (hosted on free plans, so after a quiet period the first request can take about a minute to wake the backend up). Two sample videos are built in, so you can sign up and ask a question right away.

![App screenshot](docs/screenshot.png)

## Features

- **Transcript-grounded answers.** The LLM only sees retrieved transcript chunks and cites timestamps (`MM:SS`).
- **Accounts.** Sign up and log in with bcrypt-hashed passwords and JWT access tokens.
- **Saved chats.** Every user has their own chats stored in PostgreSQL and can reopen old conversations.
- **Follow-up questions.** Each question is rewritten into a standalone search query using the conversation so far, so "tell me more about the last reason" works.
- **Ownership checks.** Every chat endpoint verifies that the chat belongs to the logged-in user.
- **Measured retrieval.** A labelled evaluation set (see below) was used to pick the chunking and retrieval settings.

## How it works

1. Fetch the video transcript with `youtube-transcript-api`.
2. Split it into chunks of about 500 characters (3-snippet overlap), keeping each chunk's start and end time.
3. Embed the chunks with Gemini (`gemini-embedding-001`) and store them in ChromaDB, one collection shared by all videos and filtered by `video_id`.
4. On each question, retrieve the top 5 chunks by vector similarity.
5. Send the chunks and the question to a Groq-hosted LLM with a prompt that restricts it to the transcript.
6. Save the question and the answer in PostgreSQL under the user's chat.

## Retrieval evaluation

I wrote 54 questions across two videos (a 24-minute Q&A talk and a 51-minute TypeScript lecture). Each question has a labelled timestamp range where the answer is spoken. A retrieved chunk counts as a hit if it overlaps that range by at least 3 seconds (or half the range, if shorter).

Metrics: **Hit@k** (the right chunk is in the top k) and **MRR** (how high it is ranked). The table shows Hit@1, Hit@5 and MRR at k=5. The chunking and reranker experiments were run with the local Qwen3-Embedding-0.6B model.

| Setup | Talk Hit@1 | Talk Hit@5 | Talk MRR | Lecture Hit@1 | Lecture Hit@5 | Lecture MRR |
|---|---|---|---|---|---|---|
| 300-char chunks | 84.6% | 100% | 0.907 | 39.3% | 92.9% | 0.596 |
| 500-char chunks | 92.3% | 100% | 0.962 | 53.6% | 100% | 0.735 |
| 800-char chunks | 96.2% | 100% | 0.974 | 57.1% | 92.9% | 0.711 |
| **500 + overlap (chosen chunking)** | 96.2% | 100% | 0.981 | 53.6% | 100% | 0.715 |
| + small reranker (FlashRank) | 65.4% | 88.5% | 0.751 | 50.0% | 85.7% | 0.632 |
| + larger reranker (MiniLM-L-12) | 88.5% | 100% | 0.926 | 53.6% | 92.9% | 0.687 |
| bge-small embeddings | 84.6% | 96.2% | 0.894 | 46.4% | 82.1% | 0.599 |
| **500 + overlap + Gemini embeddings (final)** | 92.3% | 100% | 0.952 | 85.7% | 100% | 0.923 |

What I found:

- Very small chunks (300 characters) hurt on both videos. 800 characters was about the same as 500.
- Both rerankers I tried made results worse than plain vector search on this data.
- A smaller local embedding model (bge-small) scored clearly lower than Qwen3-Embedding-0.6B.
- With Qwen3 and the chosen chunking, the right chunk is always in the top 5, but on the long lecture it is ranked first only about half the time (a neighbouring chunk often ranks higher). The app sends all 5 chunks to the LLM, so it still sees the right passage. Switching to Gemini embeddings improved this ranking problem a lot (see below).

**Final embedding model: Gemini.** The app uses Google's `gemini-embedding-001` through the Gemini API, so it does not need a local model server. With the same chunking it scored about the same as Qwen3 on the talk (Hit@1 92.3% vs 96.2%, a difference of one question) and much better on the long lecture: Hit@1 rose from 53.6% to 85.7% and MRR from 0.715 to 0.923, with Hit@5 at 100% on both videos.

Limits of this evaluation: the questions are mine, there are only two videos, and it measures retrieval, not the quality of the final answers.

## Tech stack

- **Frontend:** React, React Router, Axios, Bootstrap
- **Backend:** FastAPI, PyJWT, bcrypt, psycopg
- **Database:** PostgreSQL (users, chats, messages), ChromaDB (vectors)
- **AI:** LangChain, Groq (LLM), Google Gemini embeddings (`gemini-embedding-001`)
- **Deployment:** Docker, Render (backend), Vercel (frontend), Neon (PostgreSQL)

## Deployment

| Part | Where |
|---|---|
| React frontend | Vercel |
| FastAPI backend, built from `server/Dockerfile` | Render (free web service) |
| PostgreSQL | Neon (free) |
| Vectors | ChromaDB on the container's disk, seeded with two pre-embedded sample videos |

- The free Render plan has no persistent disk. On every start the container copies the sample videos from `server/seed_chroma` into the vector folder, so they answer instantly and cost no embedding quota. Any other video is embedded on its first question and kept only until the service restarts.
- Backend environment variables: `DATABASE_URL`, `SECRET_KEY`, `GROQ_API_KEY`, `GOOGLE_API_KEY`, `FRONTEND_ORIGIN` (the allowed website address for CORS) and `PORT`. Frontend: `VITE_API_URL` (the backend address).
- `docker-compose.yml` starts the backend and a Postgres container. `docker-compose.codespaces.yml` is a variant that uses host networking, which is the one that worked in GitHub Codespaces, where container-to-container networking was blocked.

## API

| Method | Path | Auth | Purpose |
|---|---|---|---|
| POST | `/signup` | no | Create an account |
| POST | `/login` | no | Returns a JWT access token |
| GET | `/me` | yes | The logged-in user |
| POST | `/ask` | yes | Ask a question (creates a chat, or continues one with `chat_id`) |
| GET | `/chats` | yes | List your chats |
| GET | `/chats/{chat_id}/messages` | yes | Load one of your chats |

## Run locally

**Prerequisites:** Python 3.12, Node.js, PostgreSQL, a [Groq](https://console.groq.com) API key and a [Google AI Studio](https://aistudio.google.com/apikey) API key.

1. Get a Groq API key and a Gemini API key from Google AI Studio.
2. Create a PostgreSQL database called `ytqa` and run:
   ```sql
   CREATE TABLE users (
     id SERIAL PRIMARY KEY,
     email TEXT UNIQUE NOT NULL,
     password_hash TEXT NOT NULL,
     created_at TIMESTAMP DEFAULT NOW()
   );
   CREATE TABLE chats (
     id SERIAL PRIMARY KEY,
     user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
     video_id TEXT NOT NULL,
     created_at TIMESTAMP DEFAULT NOW()
   );
   CREATE TABLE messages (
     id SERIAL PRIMARY KEY,
     chat_id INTEGER NOT NULL REFERENCES chats(id) ON DELETE CASCADE,
     role TEXT NOT NULL,
     content TEXT NOT NULL,
     created_at TIMESTAMP DEFAULT NOW()
   );
   ```
3. In `server/`, create a `.env` file:
   ```
   GROQ_API_KEY=your_groq_key
   GOOGLE_API_KEY=your_google_ai_studio_key
   DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@localhost:5432/ytqa
   SECRET_KEY=a_long_random_string
   ```
4. Start the backend:
   ```
   cd server
   python -m venv .venv
   source .venv/bin/activate   # Git Bash on Windows: source .venv/Scripts/activate
   pip install -r requirements.txt
   uvicorn main:app --reload
   ```
5. Start the frontend:
   ```
   cd client
   npm install
   npm run dev
   ```
6. Open `http://localhost:5173`, sign up, enter a YouTube video ID and ask a question. The interactive API docs are at `http://localhost:8000/docs`.

## Evaluating retrieval

`server/eval.py` runs every question in `eval_set.json` and `eval_set_ts.json` against the retriever and prints Hit@1, Hit@3, Hit@5 and MRR, plus the questions that missed.

```
cd server
python eval.py
```

## Known limitations and next steps

- Videos other than the two samples have to be embedded on their first question. On the free Gemini tier, which is rate-limited, a long video can take several minutes, and the embeddings are lost when the free Render service restarts.
- Free hosting: the backend sleeps after about 15 minutes without traffic and takes about a minute to wake up.
- The JWT is kept in `localStorage`, and tokens cannot be revoked before they expire (24 hours).
- Next: store vectors in Postgres (for example with pgvector) so they survive restarts, and test retrieval on more videos (podcasts, very long talks) to check that the results hold.