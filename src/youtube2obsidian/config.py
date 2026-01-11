from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv


@dataclass
class Settings:
    openai_api_key: Optional[str]
    litellm_model: str
    litellm_base_url: Optional[str]
    whisper_model: str
    vault_path: Path
    cache_dir: Path
    language: str = "ja"

    @classmethod
    def load(
        cls,
        *,
        vault_path: Optional[str] = None,
        cache_dir: Optional[str] = None,
        litellm_model: Optional[str] = None,
        litellm_base_url: Optional[str] = None,
        whisper_model: Optional[str] = None,
        language: str = "ja",
    ) -> "Settings":
        load_dotenv()
        openai_api_key = os.getenv("OPENAI_API_KEY")
        vault = Path(vault_path or os.getenv("VAULT_PATH", "~/Obsidian/Vault")).expanduser()
        cache = Path(cache_dir or os.getenv("CACHE_DIR", "data/cache")).expanduser()
        cache.mkdir(parents=True, exist_ok=True)
        return cls(
            openai_api_key=openai_api_key,
            litellm_model=litellm_model or os.getenv("LITELLM_MODEL", "gpt-4o-mini"),
            litellm_base_url=litellm_base_url or os.getenv("LITELLM_BASE_URL"),
            whisper_model=whisper_model or os.getenv("WHISPER_MODEL", "medium"),
            vault_path=vault,
            cache_dir=cache,
            language=language or os.getenv("LANGUAGE", "ja"),
        )
