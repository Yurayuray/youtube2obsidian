from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Optional

from .fetch import VideoMeta
from .summarize import Summary


def build_markdown(meta: VideoMeta, summary: Summary, transcript_source: str, transcript: Optional[str]) -> str:
    published = _format_date(meta.published_at)
    frontmatter = [
        "---",
        f'title: "{meta.title}"',
        f"url: {meta.url}",
        f"channel: {meta.channel}",
        f"published_at: {published}",
        "source: YouTube",
        f"transcript_source: {transcript_source}",
        "tags: [youtube, summary]",
        "---",
        "",
    ]
    body = []
    body.append("## 概要")
    body.append(summary.overview.strip())
    body.append("")
    body.append("## 主要ポイント")
    body.extend([f"- {item}" for item in summary.bullets])
    body.append("")
    body.append("## 次に知るべき内容")
    body.extend([f"- {item}" for item in summary.next_steps])
    body.append("")
    body.append("## 詳細説明")
    body.append(summary.detail.strip())
    if transcript:
        body.append("")
        body.append("## 元トランスクリプト（参考）")
        body.append("<details><summary>開く</summary>\n")
        body.append(transcript.strip())
        body.append("\n</details>")
    return "\n".join(frontmatter + body)


def save_markdown(content: str, meta: VideoMeta, vault_path: Path, overwrite: bool = False) -> Path:
    today = datetime.utcnow().strftime("%Y-%m-%d")
    folder = vault_path / "YouTube" / today[:4]
    folder.mkdir(parents=True, exist_ok=True)
    filename = f"{today} - {meta.title}.md"
    safe_name = filename.replace("/", "-")
    path = folder / safe_name
    if path.exists() and not overwrite:
        raise FileExistsError(f"{path} already exists. Use --overwrite to replace.")
    path.write_text(content, encoding="utf-8")
    return path


def _format_date(upload_date: Optional[str]) -> str:
    if not upload_date:
        return ""
    if len(upload_date) == 8:  # YYYYMMDD
        return f"{upload_date[0:4]}-{upload_date[4:6]}-{upload_date[6:8]}"
    return upload_date
