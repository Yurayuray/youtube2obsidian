from __future__ import annotations

import sys
from pathlib import Path

import litellm
import typer
from rich import print

from .config import Settings
from .fetch import TranscriptResult, download_audio, fetch_metadata, fetch_transcript
from .summarize import Summary, summarize
from .transcribe import transcribe_audio
from .writer import build_markdown, save_markdown

app = typer.Typer(add_completion=False, help="YouTube→Obsidian 要約CLI")


@app.command()
def run(
    url: str = typer.Argument(..., help="YouTubeのURL"),
    vault: Path = typer.Option(None, "--vault", "-v", help="Obsidian Vaultのパス"),
    model: str = typer.Option("gpt-4o-mini", "--model", "-m", help="litellm経由で使うモデル名"),
    whisper_model: str = typer.Option("medium", "--whisper-model", help="faster-whisperモデル"),
    cache_dir: Path = typer.Option(Path("data/cache"), "--cache-dir", help="音声/モデルキャッシュ"),
    language: str = typer.Option("ja", "--lang", help="処理・出力言語"),
    overwrite: bool = typer.Option(False, "--overwrite", help="既存ノートを上書き"),
    include_transcript: bool = typer.Option(
        False, "--include-transcript", help="Markdownに全文トランスクリプトを含める"
    ),
    no_openai: bool = typer.Option(False, "--no-openai", help="要約をスキップして全文だけ保存"),
) -> None:
    """
    YouTube動画を要約してObsidian向けMarkdownを保存します。
    """
    settings = Settings.load(
        vault_path=str(vault) if vault else None,
        cache_dir=str(cache_dir),
        litellm_model=model,
        litellm_base_url=None,
        whisper_model=whisper_model,
        language=language,
    )

    # メタ情報
    meta = fetch_metadata(url)
    print(f"[bold cyan]タイトル[/]: {meta.title}")

    # 字幕取得
    transcript: TranscriptResult | None = fetch_transcript(url, language=language)
    if transcript:
        text = transcript.text
        source = transcript.source
        print("[green]字幕を利用します[/]")
    else:
        print("[yellow]字幕なし。音声をダウンロードして文字起こしします…[/]")
        audio_path = download_audio(url, out_dir=settings.cache_dir)
        text = transcribe_audio(
            audio_path,
            model_size=settings.whisper_model,
            cache_dir=settings.cache_dir,
            language=language,
        )
        source = "whisper"

    # 要約
    if no_openai:
        summary = Summary(
            overview="要約をスキップしました（--no-openai）。",
            bullets=[],
            next_steps=[],
            detail=text,
        )
    else:
        if not settings.openai_api_key:
            print("[red]OPENAI_API_KEY が設定されていません。--no-openai を使うかキーを設定してください。[/]")
            raise typer.Exit(code=1)
        litellm.api_key = settings.openai_api_key
        if settings.litellm_base_url:
            litellm.api_base = settings.litellm_base_url
        summary = summarize(text, model=settings.litellm_model, language=language)

    # Markdown生成・保存
    md = build_markdown(
        meta=meta,
        summary=summary,
        transcript_source=source,
        transcript=text if include_transcript else None,
    )
    try:
        path = save_markdown(md, meta, settings.vault_path, overwrite=overwrite)
    except FileExistsError as exc:
        print(f"[red]{exc}[/]")
        raise typer.Exit(code=1) from exc

    print(f"[bold green]保存完了:[/] {path}")


def main() -> None:
    app()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n[red]中断しました[/]")
        sys.exit(1)
