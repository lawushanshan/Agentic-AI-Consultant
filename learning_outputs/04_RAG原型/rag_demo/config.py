import os
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


class Config:
    DEEPSEEK_API_KEY: str = os.getenv("DEEPSEEK_API_KEY", "")
    DEEPSEEK_BASE_URL: str = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
    DEEPSEEK_MODEL: str = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")

    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", os.path.join(BASE_DIR, "models", "paraphrase-multilingual-MiniLM-L12-v2"))

    CHUNK_SIZE: int = int(os.getenv("CHUNK_SIZE", "300"))
    CHUNK_OVERLAP: int = int(os.getenv("CHUNK_OVERLAP", "50"))

    TOP_K: int = int(os.getenv("TOP_K", "5"))
    RELEVANCE_THRESHOLD: float = float(os.getenv("RELEVANCE_THRESHOLD", "0.3"))

    KB_DOCS_DIR: str = os.path.join(BASE_DIR, "kb_docs")
    CHROMA_PERSIST_DIR: str = os.path.join(BASE_DIR, "chroma_db")
    PROMPTS_DIR: str = os.path.join(BASE_DIR, "prompts")
    RESULTS_DIR: str = os.path.join(BASE_DIR, "results")
