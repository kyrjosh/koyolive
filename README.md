# koyolive

博衣こよりの配信枠立てを定期的に監視し、Discord に通知するツールです。

## 仕組み

1. GitHub Actions が定期的に起動
2. Holodex API からライブ・配信予定の枠を取得
3. 未通知の枠があれば Discord に通知

## 必要な Secrets

| 名前 | 内容 |
|---|---|
| `YOUTUBE_CHANNEL_ID` | 監視するチャンネルの ID |
| `HOLODEX_API_KEY` | [Holodex](https://holodex.net) で発行した API キー |
| `DISCORD_WEBHOOK_URL` | 通知先の Discord Webhook URL |

## 謝辞

配信情報の取得に [Holodex API](https://holodex.net) を使用しています。

## 使用技術

- Python
- GitHub Actions
- Holodex API
- Discord Webhook
