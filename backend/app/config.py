import json
import os
from pathlib import Path
from typing import Annotated

from pydantic import field_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict

ROOT_DIR = Path(os.getenv("ROOT_DIR", str(Path(__file__).resolve().parents[2])))


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=ROOT_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Generic OpenAI-compatible LLM config. Defaults to Groq's free tier

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

    # NoDecode stops pydantic-settings from trying to JSON-decode this env
    # var itself (its default behavior for list-typed fields, which raises
    # a hard SettingsError — and crashes the whole app at startup — if the
    # value isn't valid JSON). Our own validator below handles both JSON
    # arrays and plain comma-separated strings.
    cors_origins: Annotated[list[str], NoDecode] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:3080",
        "http://127.0.0.1:3080",
    ]

    # Comma-separated list of additional allowed origins, e.g. a deployed
    # frontend URL: "https://rag-eval-frontend.onrender.com"
    extra_cors_origins: Annotated[list[str], NoDecode] = []

    # Same NoDecode treatment as cors_origins above, applied to both fields:
    # accept either a JSON array or a plain comma-separated string from the
    # env, instead of pydantic-settings crashing on non-JSON input.
    @field_validator("cors_origins", "extra_cors_origins", mode="before")
    @classmethod
    def _parse_origins_list(cls, value):
        if isinstance(value, str):
            stripped = value.strip()
            if stripped.startswith("["):
                try:
                    return json.loads(stripped)
                except json.JSONDecodeError:
                    pass
            return [o.strip() for o in stripped.split(",") if o.strip()]
        return value

    @property
    def all_cors_origins(self) -> list[str]:
        return self.cors_origins + self.extra_cors_origins


settings = Settings()
settings.uploads_dir.mkdir(parents=True, exist_ok=True)
settings.chroma_dir.mkdir(parents=True, exist_ok=True)
