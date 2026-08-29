from youtube_transcript_api import YouTubeTranscriptApi
from langchain_core.output_parsers import StrOutputParser
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document
from dotenv import load_dotenv

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

# embedding model
embeddings = OllamaEmbeddings(model="qwen3-embedding:0.6b")

# text splitter - makes chunks
text_splitter = RecursiveCharacterTextSplitter(chunk_size=300, chunk_overlap=50)

# vector store
vectordb = Chroma(
    collection_name="yt_transcipts",
    embedding_function=embeddings,
    persist_directory="./chroma_db",
)


def answer_question(video_id, query):
    video_id = video_id.strip()
    query = query.strip()
    result = yt_api.fetch(video_id)

    chunks = []

    current_text = ""
    chunk_start = None

    for snippet in result:

        if chunk_start is None:
            chunk_start = snippet.start

        current_text += " " + snippet.text

        if len(current_text) >= 500:

            chunks.append(
                Document(
                    page_content=current_text.strip(),
                    metadata={
                        "start": chunk_start,
                        "video_id": video_id
                    }
                )
            )

            current_text = ""
            chunk_start = None
    
    if current_text.strip():

        chunks.append(
            Document(
                page_content=current_text.strip(),
                metadata={
                    "start": chunk_start,
                    "video_id": video_id
                }
            )
        )
    
    existing = vectordb.get(where={"video_id": video_id})
    if not existing["ids"]:
        print("Adding video to database...")
        vectordb.add_documents(chunks)
    else:
        print("Video already exists. Skipping ingestion.")
    
    results = vectordb.similarity_search(
    query,
    k=5,
    filter={"video_id": video_id}
)

    context = "\n".join(
        f"Timestamp: {(int(res.metadata['start']) //60):02d}:"
        f"{(int(res.metadata['start']) % 60):02d}\n"
        f"{res.page_content}"
        for res in results
    )

    response = chain.invoke({"query": query, "context": context})
    return response
