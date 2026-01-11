from __future__ import annotations

from pathlib import Path
from typing import Optional

from faster_whisper import WhisperModel


def transcribe_audio(
    audio_path: Path,
    model_size: str = "medium",
    cache_dir: Optional[Path] = None,
    language: str = "ja",
) -> str:
    cache_path = cache_dir or Path("data/cache")
    cache_path.mkdir(parents=True, exist_ok=True)
    model = WhisperModel(model_size, download_root=str(cache_path))
    segments, _ = model.transcribe(str(audio_path), language=language)
    texts: list[str] = []
    for segment in segments:
        texts.append(segment.text.strip())
    return " ".join(texts)
