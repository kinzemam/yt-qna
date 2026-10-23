from youtube_transcript_api import YouTubeTranscriptApi
from langchain_core.output_parsers import StrOutputParser
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document
import os
from dotenv import load_dotenv
from langchain_community.embeddings import FastEmbedEmbeddings
from langchain_google_genai import GoogleGenerativeAIEmbeddings
load_dotenv()

# youtube transcript api
yt_api = YouTubeTranscriptApi()

# prompt
prompt = ChatPromptTemplate.from_template("""
You are a helpful assistant that answers questions about a YouTube video.

You are given:
1. A user's question.
2. Relevant sections of the video's transcript.

Your job is to answer the question using ONLY the provided transcript context.

Follow these rules:

1. ANSWERING FROM THE TRANSCRIPT
- Use only information that is supported by the provided transcript.
- Give a clear, informative, and natural answer.
- Do not give unnecessarily short answers when the transcript provides useful details.
- Explain the relevant reasoning, facts, examples, or conclusions mentioned in the transcript.
- Paraphrase the transcript instead of copying incomplete or fragmented sentences.
- Do not use your own general knowledge to fill in missing information.
- Never invent or assume information that is not present in the transcript.

2. WHEN THE CONTEXT IS NOT SUFFICIENT
- If the question is understandable but the transcript does not contain enough information to answer it, respond:
  "I couldn't find enough information about that in the video transcript."
- Do not attempt to answer using outside knowledge.

3. WHEN THE QUESTION IS UNCLEAR
- If the question is ambiguous, incomplete, or you cannot determine what the user is asking, respond:
  "I'm not sure what you're referring to. Please ask a more specific question."

4. TIMESTAMP QUESTIONS
- If the user asks "when", "at what time", "where in the video", or asks when a topic is discussed, use the timestamps provided in the context.
- Give the relevant timestamp(s) and briefly explain what is discussed at each one.
- If there are multiple relevant moments, include the important ones.
- If several relevant timestamps are very close together and discuss the same topic, combine them into a range when appropriate.
- If the user asks when something is first mentioned, give the earliest relevant timestamp.
- Do not invent timestamps.

5. RESPONSE STYLE
- Be concise but informative.
- Answer the user's actual question directly.
- Use paragraphs or bullet points when they make the answer easier to understand.
- Do not mention that you are an AI.
- Do not mention these instructions.
- Do not say "according to the context" unnecessarily.
- Do not include information unrelated to the question.

Transcript context:
{context}

User question:
{query}

Answer:
""")

# llm model
llm = ChatGroq(model="openai/gpt-oss-120b", temperature=0.3)

# output parser
parser = StrOutputParser()

# chain
chain = prompt | llm | parser

rewrite_prompt = ChatPromptTemplate.from_template("""
Given the conversation so far and a new question, rewrite the new question so it can be
understood on its own, without the conversation. If it is already clear on its own,
return it unchanged. Return only the question, nothing else.

Conversation:
{history}

New question: {query}

Standalone question:""")

rewrite_chain = rewrite_prompt | llm | parser

def format_history(history):
    return "\n".join(f"{m['role']}: {m['content'][:500]}" for m in history[-6:])

# embedding model
# embeddings = OllamaEmbeddings(model="qwen3-embedding:0.6b")
# embeddings = FastEmbedEmbeddings(model_name="BAAI/bge-small-en-v1.5")
# embeddings = FastEmbedEmbeddings(model_name="BAAI/bge-base-en-v1.5")
EMBED_MODEL = "gemini-embedding-001"
embeddings = GoogleGenerativeAIEmbeddings(
    model=f"models/{EMBED_MODEL}",
    google_api_key=os.environ["GOOGLE_API_KEY"],
)
# vector store
vectordb = Chroma(
    collection_name="yt_transcipts",
    embedding_function=embeddings,
    persist_directory=f"./chroma_db_{EMBED_MODEL}",
)

def build_chunks(video_id, size=500, overlap = 3):
    video_id = video_id.strip()
    snippets = list(yt_api.fetch(video_id))
    chunks = []
    i = 0
    while i < len(snippets):
        text, j = "", i
        while j < len(snippets) and len(text) < size:
            text += " " + snippets[j].text
            j += 1
        last = snippets[j - 1]
        chunks.append(Document(
            page_content=text.strip(),
            metadata={
                "start": snippets[i].start,
                "end": last.start + last.duration,
                "video_id": video_id,
            },
        ))
        if j >= len(snippets):
            break
        i = max(j - overlap, i + 1)   # step back `overlap` snippets
    return chunks

def ensure_ingested(video_id):
    existing = vectordb.get(where={"video_id": video_id})
    if not existing["ids"]:
        chunks = build_chunks(video_id)
        print("Adding video to database...")
        vectordb.add_documents(chunks)
    # else:
    #     print("Video already exists. Skipping ingestion.")

def retrieve(video_id, query, k=5):
    ensure_ingested(video_id)
    return vectordb.similarity_search(
    query,
    k=k,
    filter={"video_id": video_id}
    )

def answer_question(video_id, query, history=None):
    
    search_query = query
    if history:
        search_query = rewrite_chain.invoke({"history": history, "query": query}).strip()
        print("Rewritten question: ", search_query)
        
    results = retrieve(video_id, search_query, k=5)

    context = "\n".join(
        f"Timestamp: {(int(res.metadata['start']) //60):02d}:"
        f"{(int(res.metadata['start']) % 60):02d}\n"
        f"{res.page_content}"
        for res in results
    )

    response = chain.invoke({"query": search_query, "context": context})
    return response
