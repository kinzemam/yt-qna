#!/bin/sh
DIR=/app/chroma_db_gemini-embedding-001
mkdir -p "$DIR"
if [ -z "$(ls -A "$DIR")" ]; then
  cp -r /app/seed_chroma/. "$DIR"/
fi
exec uvicorn main:app --host 0.0.0.0 --port "${PORT:-8000}"
