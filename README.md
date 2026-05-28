# app-idea-bot

GitHub Actionsでアプリ案をBluesky / Mastodonへ投稿するための最小構成です。

## Files

- `post.py`: `posts.csv` から投稿文を読み、SNS APIへ投稿するスクリプト
- `posts.csv`: 投稿キュー
- `requirements.txt`: Python依存関係
- `.github/workflows/post.yml`: 手動実行と毎日実行のGitHub Actions workflow

## GitHub Secrets

GitHub repository settingsで以下を登録してください。

- `BLUESKY_HANDLE`
- `BLUESKY_APP_PASSWORD`
- `MASTODON_INSTANCE_URL`
- `MASTODON_ACCESS_TOKEN`

任意のRepository variables:

- `POST_TARGETS`: `bluesky,mastodon` など
- `MASTODON_VISIBILITY`: `public`, `unlisted`, `private` など

## First Run

最初はGitHub Actionsの `workflow_dispatch` で `dry_run=true` のまま実行してください。

成功したら `dry_run=false` で手動実行し、その後に `schedule` 運用へ進めます。

## Schedule

`.github/workflows/post.yml` はJST 09:00相当のUTC 00:00で実行します。

```yaml
schedule:
  - cron: "0 0 * * *"
```

GitHub Actionsのスケジュールは厳密な秒単位実行ではありません。SNS投稿用途では通常問題ありません。
