# youtube2obsidian

YouTube 動画の字幕または音声を取得し、要約を生成して Obsidian 用 Markdown ノートに保存する CLI ツールです。字幕がない場合は `yt-dlp` で音声をダウンロードし、`faster-whisper` で文字起こしします。要約には `litellm` 経由で OpenAI 互換モデルを利用します。

## クイックスタート
```bash
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
cp .env.example .env   # 必要なキー/パスを設定
```

## 必要な環境変数 (`.env`)
```
OPENAI_API_KEY=your_api_key_here
LITELLM_MODEL=gpt-4o-mini
LITELLM_BASE_URL=
WHISPER_MODEL=medium
VAULT_PATH=~/Obsidian/Vault
CACHE_DIR=data/cache
LANGUAGE=ja
```

## 使い方
```bash
youtube2obsidian https://youtu.be/VIDEO_ID
```
`.env` に `VAULT_PATH`, `LITELLM_MODEL`, `WHISPER_MODEL`, `LANGUAGE` を設定しておけば URL だけで実行できます。全文トランスクリプト埋め込みはデフォルトで有効です（不要なら `--no-include-transcript`）。

主なオプション:
- `--vault/-v PATH` : 保存先 Obsidian Vault パス（未指定時は環境変数）。
- `--model/-m NAME` : 要約に使う litellm モデル。
- `--whisper-model NAME` : faster-whisper のモデルサイズ。
- `--cache-dir PATH` : 音声・モデルキャッシュ。
- `--lang CODE` : 処理/出力言語（デフォルト ja）。
- `--overwrite` : 同名ノートを上書き。
- `--include-transcript / --no-include-transcript` : ノート末尾に全文トランスクリプトを含める（デフォルトで含める）。
- `--no-openai` : 要約せず全文のみ保存。

## 出力
- 保存先: `<vault>/YouTube/<YYYY>/<YYYY-MM-DD> - <Title>.md`
- Frontmatter: `title, url, channel, published_at, source, transcript_source, tags`
- セクション: `概要 / 主要ポイント / 次に知るべき内容 / 詳細説明`（必要に応じてトランスクリプト折りたたみ）

## 開発・テスト
```bash
ruff check .
pytest
```
ネットワーク・LLM 呼び出しはテストでモックする想定です。キャッシュは `data/cache/` に作成され、`.gitignore` 済みです。
