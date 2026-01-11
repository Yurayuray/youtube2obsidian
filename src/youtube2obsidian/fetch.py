from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import yt_dlp
from youtube_transcript_api import NoTranscriptFound, YouTubeTranscriptApi


@dataclass
class VideoMeta:
    title: str
    channel: str
    published_at: Optional[str]
    duration: Optional[int]
    url: str


@dataclass
class TranscriptResult:
    text: str
    source: str  # "subtitles" | "whisper"


def fetch_metadata(url: str) -> VideoMeta:
    ydl_opts = {"quiet": True, "skip_download": True, "no_warnings": True, "noplaylist": True}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
    return VideoMeta(
        title=info.get("title", "untitled"),
        channel=info.get("uploader", "unknown"),
        published_at=info.get("upload_date"),
        duration=info.get("duration"),
        url=url,
    )


def fetch_transcript(url: str, language: str = "ja") -> Optional[TranscriptResult]:
    """
    Try to fetch subtitles from YouTube. Returns None if unavailable.
    """
    video_id = _extract_video_id(url)
    try:
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
        # Prefer requested language then English
        for lang_code in (language, "ja", "en"):
            try:
                transcript = transcript_list.find_transcript([lang_code])
                entries = transcript.fetch()
                text = " ".join(item["text"] for item in entries if item.get("text"))
                return TranscriptResult(text=text, source="subtitles")
            except NoTranscriptFound:
                continue
    except Exception:
        return None
    return None


def download_audio(url: str, out_dir: Path) -> Path:
    """
    Download audio only. Returns path to file.
    """
    out_dir.mkdir(parents=True, exist_ok=True)
    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": str(out_dir / "%(id)s.%(ext)s"),
        "quiet": True,
        "no_warnings": True,
        "noplaylist": True,
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }
        ],
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        filename = ydl.prepare_filename(info)
    # after postprocessor, extension is mp3
    mp3_path = Path(Path(filename).with_suffix(".mp3"))
    return mp3_path


def _extract_video_id(url: str) -> str:
    if "youtube.com/watch" in url and "v=" in url:
        return url.split("v=")[1].split("&")[0]
    if "youtu.be/" in url:
        return url.split("youtu.be/")[1].split("?")[0]
    return url
