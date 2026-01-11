from __future__ import annotations

from dataclasses import dataclass
from typing import List

import litellm
import tiktoken


@dataclass
class Summary:
    overview: str
    bullets: List[str]
    next_steps: List[str]
    detail: str


def _encode_length(text: str, model: str = "gpt-4o-mini") -> int:
    try:
        enc = tiktoken.encoding_for_model(model)
    except Exception:
        enc = tiktoken.get_encoding("cl100k_base")
    return len(enc.encode(text))


def chunk_text(text: str, model: str, max_tokens: int = 3000, overlap: int = 200) -> List[str]:
    tokens = text.split()
    chunks: List[str] = []
    current: list[str] = []
    current_len = 0
    for word in tokens:
        current.append(word)
        current_len += _encode_length(word, model=model)
        if current_len >= max_tokens:
            chunk = " ".join(current)
            chunks.append(chunk)
            # overlap
            overlap_words = current[-overlap:] if overlap < len(current) else current
            current = overlap_words.copy()
            current_len = sum(_encode_length(w, model=model) for w in current)
    if current:
        chunks.append(" ".join(current))
    return chunks


def _summarize_chunk(chunk: str, model: str, language: str) -> str:
    prompt = (
        f"次のテキストを{language}で簡潔に要約してください。"
        " 箇条書きは不要で、3行以内の短い要約だけ返してください。\n\n"
        f"テキスト:\n{chunk}"
    )
    resp = litellm.completion(
        model=model,
        messages=[
            {"role": "system", "content": "あなたは有能な要約者です。"},
            {"role": "user", "content": prompt},
        ],
    )
    return resp.choices[0].message["content"].strip()


def summarize(text: str, model: str, language: str = "ja") -> Summary:
    litellm.drop_params = True  # silence warnings for unknown params
    chunks = chunk_text(text, model=model)
    partials = [_summarize_chunk(chunk, model=model, language=language) for chunk in chunks]
    merged = "\n".join(partials)

    final_prompt = (
        "以下のまとめを基に、4つのセクションを日本語で作成してください。\n"
        "1) 概要: 3-5行\n"
        "2) 主要ポイント: 箇条書き5-8件\n"
        "3) 次に知るべき内容: 箇条書き3-5件\n"
        "4) 詳細説明: 簡潔な段落（7-10文以内）\n"
        "原文にない推測は避け、重要度順に並べてください。\n\n"
        f"素材となるまとめ:\n{merged}"
    )
    resp = litellm.completion(
        model=model,
        messages=[
            {"role": "system", "content": "あなたは精度重視の技術要約者です。"},
            {"role": "user", "content": final_prompt},
        ],
    )
    content = resp.choices[0].message["content"]
    # 粗いパース：セクション見出しで分割
    overview = _extract_section(content, ["概要", "要約", "Summary"])
    bullets = _extract_list(content, ["主要ポイント", "ポイント", "Key Points"])
    next_steps = _extract_list(content, ["次に知るべき内容", "Next", "Further Reading"])
    detail = _extract_section(content, ["詳細", "詳細説明", "Detail"])
    return Summary(
        overview=overview.strip() or content.strip(),
        bullets=bullets or [overview.strip()],
        next_steps=next_steps,
        detail=detail.strip(),
    )


def _extract_section(text: str, keys: List[str]) -> str:
    lower = text.splitlines()
    buf: list[str] = []
    capture = False
    for line in lower:
        if any(k in line for k in keys):
            capture = True
            continue
        if capture and line.strip().startswith("##"):
            break
        if capture:
            buf.append(line)
    return "\n".join(buf).strip()


def _extract_list(text: str, keys: List[str]) -> List[str]:
    lines = text.splitlines()
    buf: list[str] = []
    capture = False
    for line in lines:
        if any(k in line for k in keys):
            capture = True
            continue
        if capture and line.strip().startswith("##"):
            break
        if capture and line.strip().startswith(("-", "・", "*")):
            buf.append(line.strip("- ・*").strip())
    return buf
