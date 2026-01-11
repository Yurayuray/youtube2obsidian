# 実装プラン (YouTube → Obsidian 要約パイプライン)

## 目的
YouTube動画のURLを入力すると、可能なら字幕を取得し、なければ音声をダウンロードして文字起こしし、要約（概要・ポイント列挙・次に知るべき内容・詳細説明）を生成して Obsidian Vault にMarkdown保存するCLIを提供する。

## 使用ライブラリ・ツール
- `youtube-transcript-api`: 公開字幕の取得に使用。字幕が得られた場合は音声ダウンロードと文字起こしを省略。
- `yt-dlp`: 字幕が無い場合の音声ダウンロードに使用（音声のみでサイズ削減）。
- `faster-whisper`: ローカルで高速文字起こしを実行。モデルは環境変数またはCLIオプションで指定（例: `medium`）。キャッシュディレクトリを再利用。
- `litellm`: OpenAI互換の推論呼び出しラッパ。`OPENAI_API_KEY` などを `.env` で管理。
- `typer` または `click`: CLI構築。

## 処理フロー
1. URL受領 → メタ情報取得（タイトル・チャンネル・公開日）。
2. `youtube-transcript-api` で字幕取得を試行。
3. 失敗した場合のみ `yt-dlp` で音声DL → `faster-whisper` で文字起こし。
4. テキストをチャンク化（トークン上限対策）→ litellm 経由で各チャンク要約 → 再要約で統合。
5. 生成物:  
   - 概要（3-5行）  
   - 主要ポイント箇条書き  
   - 次に知るべき内容 / 深掘り箇条書き  
   - 詳細な全体説明（短い段落）  
6. Obsidian向けMarkdownをテンプレート化して保存。

## CLI仕様（例）
- `python -m youtube2obsidian.cli <YouTube URL> --vault ~/Obsidian/Vault --model gpt-4o-mini --whisper-model medium --lang ja --overwrite`
- オプション: `--cache-dir data/cache`, `--timeout`, `--max-tokens`, `--no-openai`（要約をスキップし全文保存するデグレード）。
- `--include-transcript/--no-include-transcript`: デフォルトは含める。不要な場合のみ `--no-include-transcript` を指定。

## 出力フォーマット
- 保存先: `<vault>/YouTube/<YYYY>/<YYYY-MM-DD> - <Title>.md`
- Frontmatter例: `title, url, channel, published_at, source: YouTube, tags: [youtube, summary], transcript_source: subtitles|whisper`
- 本文ブロック: `## 概要`, `## 主要ポイント`, `## 次に知るべき内容`, `## 詳細説明`, `## 元トランスクリプト`（省略可/折りたたみ）。

## 環境・設定
- `.env.example` に `OPENAI_API_KEY`, `LITELLM_MODEL`, `WHISPER_MODEL`, `VAULT_PATH`, `CACHE_DIR` を記載。
- `data/cache/` を `.gitignore` に追加（音声・モデル・一時ファイル）。

## エラー/リトライ方針
- 字幕取得失敗 → 音声DLにフォールバック。  
- Whisper失敗時: 再試行（回数指定）。  
- OpenAI呼び出しはレート制御と指数バックオフを実装。  
- 途中成果を一時ファイルに残し再開可能にする。

## テスト
- `pytest`：モジュール単体テスト（字幕取得、チャンク分割、テンプレ整形）。  
- ネットワーク/LLMは `responses` やモックで固定化。  
- 短尺テスト動画で統合スモーク（音声DL→Whisper→要約→ファイル生成）をスキップ可フラグ付きで実行。

## 自動化・運用
- ファイル監視（例: `watchdog`）でURLリストを処理するスクリプトは `scripts/` に分離。  
- コスト管理: OpenAIモデルはデフォルトで軽量版、環境変数で切替。  
- ログ: `logging` でJSON風1行ログを標準出力へ（Obsidian側のメモ汚染を防止）。
