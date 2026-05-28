# app-idea-bot

GitHub Actionsでアプリ案をBluesky / Mastodonへ投稿するための最小構成です。

## Files

- `post.py`: `posts.csv` から投稿文を読み、設定済みSNSへ投稿するスクリプト
- `posts.csv`: 投稿キュー
- `requirements.txt`: Python依存関係
- `.github/workflows/post.yml`: 手動実行と毎日実行のGitHub Actions workflow

## Current Plan

Mastodonは承認待ちの間、Blueskyだけ先に動かせます。

`post.py` は対象SNSごとに必要な環境変数を確認し、未設定のSNSはスキップします。

```text
BLUESKY_* がある -> Blueskyに投稿
MASTODON_* がない -> Mastodonはスキップ
DRY_RUN=true -> 実投稿せず、投稿予定先だけログに出す
```

## GitHub Secrets

Blueskyを先に動かす場合は、まず以下だけ登録してください。

- `BLUESKY_HANDLE`
- `BLUESKY_APP_PASSWORD`

Mastodon承認後に以下を追加します。

- `MASTODON_INSTANCE_URL`
- `MASTODON_ACCESS_TOKEN`

任意のRepository variables:

- `POST_TARGETS`: `bluesky`, `mastodon`, `bluesky,mastodon` など。未設定時は `bluesky,mastodon`
- `MASTODON_VISIBILITY`: `public`, `unlisted`, `private` など。未設定時は `public`

## First Run

最初はGitHub Actionsの `workflow_dispatch` で `dry_run=true` のまま実行してください。

Bluesky Secretsが入っている場合、ログは次のようになります。

```text
Selected post: idea-001
...
Skipping mastodon: missing MASTODON_INSTANCE_URL or MASTODON_ACCESS_TOKEN
DRY_RUN=true; would post to: bluesky
No external API calls were made.
```

その後、`dry_run=false` で手動実行し、Blueskyだけ実投稿テストします。

Mastodonはサーバー承認後にアクセストークンを作成してから追加します。

## Schedule

`.github/workflows/post.yml` はJST 09:00相当のUTC 00:00で実行します。

```yaml
schedule:
  - cron: "0 0 * * *"
```

GitHub Actionsのスケジュールは厳密な秒単位実行ではありません。SNS投稿用途では通常問題ありません。
