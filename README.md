# AI Viral Content Bot

Automated daily pipeline that generates **15 viral AI scripts/day** for Persian-language Instagram channels — real-time trend research, LLM script generation, and structured Telegram delivery.

Runs on a daily cron job. Zero manual intervention required after setup.

---

## How It Works

```
Claude Web Search API        →   Fetch latest AI trends (last 48h, 7d, 30d)
        ↓
Scenario Rotation Engine     →   Pick 15 unique content scenarios
        ↓
Batch Claude Generation      →   Generate scripts in groups of 4
        ↓
Persistent Memory Check      →   Filter out repeated topics/hooks
        ↓
Telegram Delivery            →   Formatted pack sent to channel
```

---

## Features

- **Real-time trend research** — Claude web-search API fetches viral AI news across 3 time windows
- **16 scenario types** — طنز، خبر داغ، درام، ابزار جدید، آموزش، بحث‌برانگیز، کلاهبرداری و...
- **Persistent memory** — tracks 40+ used topics and hooks across days, zero repetition
- **Fault-tolerant** — checkpoint recovery system resumes interrupted runs from last saved state
- **Instagram algorithm aware** — prompts engineered around shares, watch time, save triggers
- **Batch processing** — generates in groups of 4 to stay within rate limits
- **Retry logic** — failed Telegram sends automatically retried at end of run

---

## Output Per Script

Each of the 15 daily ideas includes:

| Field | Description |
|-------|-------------|
| `hook` | Opening line — personal moment or shocking statement |
| `script` | 45-second script with timestamps `[0-5]`, `[5-15]`... |
| `caption` | Instagram caption with Persian hashtags |
| `cta` | Debate-driving question |
| `thumbnail_text` | Max 5 Persian words |
| `viral_score` | 1–10 estimated virality |
| `difficulty` | easy / medium / hard |
| `share_trigger` | Why someone would share this to a friend |

---

## Setup

```bash
# Clone
git clone https://github.com/abolhassani-dev/ai-viral-content-bot
cd ai-viral-content-bot

# Install dependencies
pip install requests

# Configure environment
cp .env.example .env
# Fill in your API keys in .env

# Run manually
python content_bot.py

# Or schedule daily via cron
0 8 * * * cd /path/to/bot && python content_bot.py >> /var/log/content_bot.log 2>&1
```

---

## Environment Variables

```env
ANTHROPIC_API_KEY=sk-ant-...
TELEGRAM_BOT_TOKEN=...
TELEGRAM_CHANNEL_ID=-100...
```

---

## Tech Stack

- **Python 3.10+**
- **Anthropic API** — Claude Sonnet for trend fetching (web search) and batch script generation
- **Telegram Bot API** — delivery and formatting
- **JSON** — persistent memory and checkpoint files

---

## Project Structure

```
├── content_bot.py        # Main pipeline
├── content_memory.json   # Persistent topic/hook memory (auto-generated)
├── content_ideas.json    # Daily checkpoint file (auto-generated)
├── .env.example          # Environment variable template
└── README.md
```

---

## Notes

- Scripts are written in **natural conversational Persian (Tehrani dialect)**
- All content is designed for **45-second Instagram Reels**
- The bot never publishes autonomously — all scripts are delivered to Telegram for human review before recording
