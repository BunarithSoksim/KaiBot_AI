FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# CHROMA_PERSIST_DIR (config.py) resolves to /app/chroma_store -- mount the
# platform's persistent disk here so the vector index survives restarts/
# redeploys instead of being rebuilt (and re-billed against the Gemini
# embedding API) every time the container starts fresh.
VOLUME ["/app/chroma_store"]

EXPOSE 8000

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
