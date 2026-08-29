# YouTube Q&A

An AI-powered application that lets you ask questions about the content of a YouTube video.

The application retrieves the video's transcript, creates searchable vector embeddings, retrieves the most relevant parts of the transcript for a user's question, and uses an LLM to generate a grounded answer.

## Features

- Ask questions about YouTube videos using a video ID
- Automatically fetch YouTube transcripts
- Chunk transcripts while preserving timestamps
- Semantic search over transcript content
- Retrieval-Augmented Generation (RAG)
- Chroma vector database for persistent storage
- Qwen3 embeddings through Ollama
- Groq LLM for answer generation
- Embedded YouTube video player
- Timestamp-aware answers
- React frontend with FastAPI backend

## Tech Stack

| Part | Technology |
|---|---|
| Frontend | React, Axios, React Markdown, CSS |
| Backend | Python, FastAPI, Uvicorn |
| LLM | Groq |
| Embeddings | Qwen3 Embedding (`qwen3-embedding:0.6b`) |
| Vector Database | Chroma |
| RAG Framework | LangChain |
| Transcript | YouTube Transcript API |
| Local Model Runtime | Ollama |

## How It Works

```text
                User
                 |
                 v
        React Frontend
                 |
          Video ID + Question
                 |
                 v
            FastAPI
                 |
                 v
        YouTube Transcript
                 |
                 v
       Transcript Chunking
        + Timestamp Metadata
                 |
                 v
          Qwen Embeddings
                 |
                 v
          Chroma Database
                 |
                 | Semantic Search
                 v
       Relevant Transcript Chunks
                 |
                 v
            Groq LLM
                 |
                 v
             Answer
                 |
                 v
        React Frontend
```

### RAG Process

When a user asks a question:

1. The YouTube transcript is retrieved.
2. The transcript is divided into meaningful chunks.
3. Each chunk is converted into an embedding using Qwen3.
4. The embeddings are stored in Chroma.
5. The user's question is used to find the most relevant transcript chunks.
6. The retrieved chunks are provided to the Groq LLM as context.
7. The LLM generates an answer based on the retrieved transcript.
8. Transcript timestamps can be used to identify where the relevant information appears in the video.

## Project Structure

```text
yt-transcript/
│
├── client/
│   ├── src/
│   │   ├── components/
│   │   ├── services/
│   │   ├── App.jsx
│   │   └── App.css
│   ├── package.json
│   └── ...
│
├── server/
│   ├── main.py
│   ├── rag.py
│   ├── requirements.txt
│   └── ...
│
├── .gitignore
└── README.md
```

## Requirements

Before running the project, make sure you have:

- Python 3.10+
- Node.js and npm
- Ollama
- A Groq API key

## Installation

### 1. Clone the repository

```bash
git clone <your-repository-url>
cd yt-transcript
```

### 2. Set up the backend

```bash
cd server
python -m venv venv
```

Activate the virtual environment.

**Windows:**

```bash
venv\Scripts\activate
```

**Linux/macOS:**

```bash
source venv/bin/activate
```

Install the Python dependencies:

```bash
pip install -r requirements.txt
```

### 3. Set up Ollama

Pull the embedding model:

```bash
ollama pull qwen3-embedding:0.6b
```

Make sure Ollama is running before using the application.

### 4. Configure environment variables

Create a `.env` file inside the `server` directory:

```env
GROQ_API_KEY=your_groq_api_key
```

Do not commit your `.env` file to GitHub.

### 5. Start the backend

From the `server` directory:

```bash
uvicorn main:app --reload
```

The FastAPI server will run at:

```text
http://127.0.0.1:8000
```

API documentation is available at:

```text
http://127.0.0.1:8000/docs
```

### 6. Start the frontend

Open a new terminal:

```bash
cd client
npm install
npm run dev
```

The React development server will normally be available at:

```text
http://localhost:5173
```

## API

### `POST /ask`

Accepts a YouTube video ID and a question.

#### Request

```json
{
  "video_id": "OL3Vj56ftWM",
  "query": "What does the speaker say about time travel?"
}
```

#### Response

```json
{
  "answer": "The speaker explains that..."
}
```

## Example

A user can enter a video ID such as:

```text
OL3Vj56ftWM
```

and ask:

```text
What does the speaker say about time travel?
```

The system retrieves relevant transcript sections and generates an answer based on those sections.

For questions such as:

```text
At what time does Brian talk about asteroids?
```

the system can use the timestamp metadata associated with retrieved transcript chunks to identify relevant moments in the video.

## Environment Variables

| Variable | Required | Description |
|---|---|---|
| `GROQ_API_KEY` | Yes | API key for the Groq LLM |

## Important Notes

- The YouTube video must have an accessible transcript.
- Ollama must be running locally because it is used for embeddings.
- The Chroma database is stored locally.
- The application currently expects a YouTube video ID.
- The quality of the answers depends on transcript quality and retrieval quality.

## Future Improvements

- [ ] Accept full YouTube URLs
- [ ] Add clickable timestamps
- [ ] Jump the embedded video to referenced timestamps
- [ ] Improve retrieval and ranking
- [ ] Add conversation history
- [ ] Add streaming responses
- [ ] Improve error handling
- [ ] Add mobile-responsive layouts
- [ ] Deploy the application
- [ ] Add authentication
- [ ] Add user-specific video history

## License

This project is intended for educational and portfolio purposes.
