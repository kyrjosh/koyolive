import os
import json
import requests
from datetime import datetime, timezone
from pathlib import Path

CHANNEL_ID = os.environ["YOUTUBE_CHANNEL_ID"]
HOLODEX_API_KEY = os.environ["HOLODEX_API_KEY"]
DISCORD_WEBHOOK_URL = os.environ["DISCORD_WEBHOOK_URL"]

STATE_FILE = Path("notified.json")


def fetch_live_videos() -> list[dict]:
    resp = requests.get(
        "https://holodex.net/api/v2/users/live",
        headers={"X-APIKEY": HOLODEX_API_KEY},
        params={"channels": CHANNEL_ID},
        timeout=15,
    )
    resp.raise_for_status()
    return resp.json()


def load_notified() -> list[str]:
    if STATE_FILE.exists():
        return json.loads(STATE_FILE.read_text())
    return []


def save_notified(notified: list[str]) -> None:
    STATE_FILE.write_text(json.dumps(notified[-100:]))


def post_to_discord(video: dict) -> None:
    vid = video["id"]
    title = video.get("title", "（タイトル不明）")
    channel_name = video.get("channel", {}).get("name", "")
    status = video.get("status", "upcoming")

    start_at = video.get("start_scheduled") or video.get("start_actual") or ""
    if start_at:
        ts = int(datetime.fromisoformat(start_at.replace("Z", "+00:00")).timestamp())
        start_display = f"<t:{ts}:F>（<t:{ts}:R>）"
    else:
        start_display = "未定"

    requests.post(
        DISCORD_WEBHOOK_URL,
        json={
            "content": f"@everyone **{channel_name}** が配信枠を立てました。",
            "embeds": [
                {
                    "title": title,
                    "url": f"https://youtu.be/{vid}",
                    "color": 0xFF0000 if status == "live" else 0x1DB954,
                    "fields": [
                        {
                            "name": "ステータス",
                            "value": "🔴 配信中" if status == "live" else "📅 配信予定",
                            "inline": True,
                        },
                        {"name": "開始時刻", "value": start_display, "inline": True},
                    ],
                    "image": {"url": f"https://i.ytimg.com/vi/{vid}/maxresdefault.jpg"},
                    "footer": {"text": "YouTube Live Monitor (Holodex)"},
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                }
            ],
        },
        timeout=15,
    ).raise_for_status()


def main():
    videos = fetch_live_videos()
    notified = load_notified()

    for video in videos:
        vid = video.get("id", "")
        if not vid or video.get("status") == "past" or vid in notified:
            continue
        print(f"新規枠を検出: {video.get('title', '')}")
        post_to_discord(video)
        notified.append(vid)
        print("通知完了")

    save_notified(notified)


if __name__ == "__main__":
    main()
