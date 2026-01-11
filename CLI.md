# CLI 利用ガイド (youtube2obsidian)

## コマンド概要
`youtube2obsidian` は Typer ベースのCLIで、YouTube URLを指定して要約ノートをObsidian Vaultに保存します。  
インストール後に `youtube2obsidian` または `python -m youtube2obsidian.cli` で呼び出せます。

## 基本の呼び出し例
```bash
youtube2obsidian https://youtu.be/VIDEO_ID \
  --vault ~/Obsidian/Vault \
  --model gpt-5.2 \
  --whisper-model medium \
  --lang ja \
  --include-transcript
```

## 主要オプション
- `url` (必須, 引数) : 処理したい YouTube の URL。
- `--vault / -v PATH` : 出力先 Obsidian Vault のパス。未指定時は環境変数 `VAULT_PATH` を使用。
- `--model / -m NAME` : litellm 経由で呼び出すモデル名（例: `gpt-4o-mini`）。未指定時は `LITELLM_MODEL` またはデフォルト。
- `--whisper-model NAME` : faster-whisper モデルサイズ（例: `medium`, `large-v2`）。未指定時は `WHISPER_MODEL` またはデフォルト。
- `--cache-dir PATH` : 音声・モデルのキャッシュディレクトリ。デフォルト `data/cache`。
- `--lang CODE` : 処理言語。デフォルト `ja`。
- `--overwrite` : 既存の同名ノートがある場合に上書き保存。
- `--include-transcript` : 生成ノートに全文トランスクリプトを折りたたみセクションとして含める。
- `--no-openai` : 要約をスキップし全文のみ保存（OpenAIキーなし運用向け）。

## 典型的な使い方
- 字幕がある動画を要約だけ保存:  
  `youtube2obsidian https://youtu.be/abc123 --vault ~/Obsidian/Vault`
- 字幕が無い動画で全文も残したい:  
  `youtube2obsidian https://youtu.be/def456 --include-transcript --vault ~/Obsidian/Vault`
- 既存ノートを更新したい:  
  `youtube2obsidian https://youtu.be/ghi789 --overwrite --vault ~/Obsidian/Vault`
- 軽量モデルでコストを抑えたい:  
  `youtube2obsidian https://youtu.be/jkl012 --model gpt-4o-mini --whisper-model small`
- 要約せず全文だけ欲しい:  
  `youtube2obsidian https://youtu.be/mno345 --no-openai --include-transcript`

## 環境変数（`.env` 例）
```
OPENAI_API_KEY=your_api_key_here
LITELLM_MODEL=gpt-4o-mini
LITELLM_BASE_URL=
WHISPER_MODEL=medium
VAULT_PATH=~/Obsidian/Vault
CACHE_DIR=data/cache
LANGUAGE=ja
```

## 出力先とファイル名
- 保存先: `<vault>/YouTube/<YYYY>/<YYYY-MM-DD> - <Title>.md`
- 上書き防止のため、同名ファイルがある場合は `--overwrite` が必要です。
