from dotenv import load_dotenv
import os

# Load .env if present
load_dotenv()

# Ollama configuration
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
MODEL_NAME = os.getenv("MODEL_NAME", "gpt-oss:20b")

# Preferred model priority (comma separated). The RAG code will pick the first
# model present on the local Ollama host. Keep gpt-oss in the list for future use
# but fall back to smaller models like codellama:7b or llama3.1:8b.
MODEL_PREFERENCE = os.getenv(
    "MODEL_PREFERENCE",
    "gpt-oss:20b,codellama:13b,codellama:7b,llama3.1:8b,llava:13b",
)

# Parsed list form
PREFERRED_MODELS = [m.strip() for m in MODEL_PREFERENCE.split(",") if m.strip()]

# Embedding model used by the RAG pipeline
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
