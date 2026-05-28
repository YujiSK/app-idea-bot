# Codex Automations 設定まとめ

作成日: 2026-05-28

## 目的

`app-idea-bot` のBluesky自動投稿が、GitHub Actionsで毎日JST 09:00頃に正しく実行されているかを、最初の3日間だけCodex Automationsで確認する。

投稿処理そのものはGitHub Actionsに任せ、Codex Automationsは投稿後の監視・確認・報告に使う。

## 作成したAutomation

Automation ID:

```text
check-app-idea-bot-posts
```

実行スケジュール:

```text
2026-05-29 09:10 JST から毎日、3回
```

## 確認対象

GitHubリポジトリ:

```text
YujiSK/app-idea-bot
```

GitHub Actions workflow:

```text
Auto Post App Ideas
```

Bluesky公開プロフィール:

```text
https://bsky.app/profile/ideatomvp.bsky.social
```

## Codex Automationsで確認する内容

- GitHub ActionsがJST 09:00前後に実行されたか
- workflowがsuccessになっているか
- Actionsログに `Posted to Bluesky` があるか
- Mastodon未設定時に想定通りskipされているか
- `posts.csv` が更新されているか
- 投稿済みステータス更新に伴う自動commit/pushがあるか
- 同じ投稿が二重投稿されていないか
- Bluesky公開プロフィールに新しい投稿が表示されているか
- 最新投稿の時刻が妥当か
- Bluesky上でも重複投稿が見えないか

## 報告フォーマット

毎回、次の形式でこのスレッドに報告する。

```text
app-idea-bot 自動投稿監視結果

日付:
確認時刻:

GitHub Actions:
- 実行有無:
- 実行時刻:
- 結果:
- Posted to Bluesky:
- Mastodon skip:
- 自動commit/push:

posts.csv:
- 投稿されたID:
- status更新:
- 二重投稿の疑い:

Bluesky:
- 最新投稿確認:
- 最新投稿時刻:
- 重複投稿:

総合判定:
OK / 要確認 / NG

メモ:
```

## 使い分け

GitHub Actions:

```text
毎日09:00にSNS投稿を実行する本番処理
```

Codex Automations:

```text
投稿後にActions、ログ、posts.csv、Bluesky公開プロフィールを確認して、このスレッドに報告する監視役
```

## 期待する運用

1. 今日: 追加作業はしない
2. 明日09:10頃: 1回目の自動確認
3. 2日目09:10頃: 2回目の自動確認
4. 3日目09:10頃: 3回目の自動確認
5. 3日分の結果を見て、投稿文や運用方針を微調整する

## 補足

Mastodonは承認待ちのため、現時点ではBluesky先行運用とする。

Mastodon承認後は、以下のSecretsを追加し、dry-runから確認する。

```text
MASTODON_INSTANCE_URL
MASTODON_ACCESS_TOKEN
```
