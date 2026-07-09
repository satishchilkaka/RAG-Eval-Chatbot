import os
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT_DIR = Path(os.getenv("ROOT_DIR", str(Path(__file__).resolve().parents[2])))


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=ROOT_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Generic OpenAI-compatible LLM config. Defaults to Groq's free tier
    # (no credit card needed): https://console.groq.com/keys
    llm_api_key: str = ""
    llm_base_url: str = "https://api.groq.com/openai/v1"
    llm_model: str = "llama-3.3-70b-versatile"

    embedding_model: str = "onnx-MiniLM-L6-v2"
    chunk_size: int = 500
    chunk_overlap: int = 50
    top_k: int = 4

    uploads_dir: Path = ROOT_DIR / "data" / "uploads"
    chroma_dir: Path = ROOT_DIR / "data" / "chroma"
    collection_name: str = "documents"

    cors_origins: list[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:3080",
        "http://127.0.0.1:3080",
    ]
    # Comma-separated list of additional allowed origins, e.g. a deployed
    # frontend URL: "https://rag-eval-frontend.onrender.com"
    extra_cors_origins: str = ""

    @property
    def all_cors_origins(self) -> list[str]:
        extra = [o.strip() for o in self.extra_cors_origins.split(",") if o.strip()]
        return self.cors_origins + extra


settings = Settings()
settings.uploads_dir.mkdir(parents=True, exist_ok=True)
settings.chroma_dir.mkdir(parents=True, exist_ok=True)
