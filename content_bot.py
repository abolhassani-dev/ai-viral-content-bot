#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json, requests, random, os, re, time
from datetime import datetime

# ============================================================
# CONFIGURATION — set these as environment variables
# cp .env.example .env  →  fill in your values  →  source .env
# ============================================================
ANTHROPIC_API_KEY   = os.environ.get("ANTHROPIC_API_KEY", "")
TELEGRAM_BOT_TOKEN  = os.environ.get("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHANNEL_ID = os.environ.get("TELEGRAM_CHANNEL_ID", "")

IDEAS_PER_DAY = 15
MEMORY_FILE   = "content_memory.json"
IDEAS_FILE    = "content_ideas.json"

SCENARIOS = [
    {"id": "fun",          "name": "طنز و میم",        "type": "emotional",   "desc": "funny relatable AI content",                                           "hook": "funny unexpected relatable"},
    {"id": "news",         "name": "خبر داغ",           "type": "emotional",   "desc": "latest viral AI news and launches",                                    "hook": "urgent shocking breaking"},
    {"id": "drama",        "name": "درام",               "type": "emotional",   "desc": "AI controversies and firings",                                         "hook": "dramatic emotional"},
    {"id": "product",      "name": "ابزار جدید",        "type": "emotional",   "desc": "new AI tool reviews, demos and comparisons",                           "hook": "curiosity comparison discovery"},
    {"id": "howto",        "name": "آموزش کاربردی",    "type": "educational", "desc": "practical AI tutorials for everyday life and business",                "hook": "practical useful step-by-step"},
    {"id": "controversial","name": "بحث‌برانگیز",      "type": "emotional",   "desc": "hot AI debates and provocative takes",                                 "hook": "provocative bold divisive"},
    {"id": "curiosity",    "name": "کنجکاوی‌محور",     "type": "emotional",   "desc": "mind-blowing AI facts and what-if scenarios",                         "hook": "mysterious curiosity what-if"},
    {"id": "story",        "name": "داستان سریالی",     "type": "emotional",   "desc": "serialized stories where AI changes someone's life with cliffhanger", "hook": "story-driven suspenseful cliffhanger"},
    {"id": "scam",         "name": "کلاهبرداری و خطر", "type": "emotional",   "desc": "AI scams, deepfakes, frauds, fake calls and security dangers",        "hook": "fear shocking dangerous"},
    {"id": "comparison",   "name": "جنگ مدل‌ها",       "type": "emotional",   "desc": "GPT vs Claude vs Gemini rivalries and comparisons",                   "hook": "competitive controversial comparison"},
    {"id": "jobs",         "name": "شغل و درآمد",       "type": "emotional",   "desc": "how AI affects jobs, careers, freelancing and money",                 "hook": "money fear opportunity"},
    {"id": "experiment",   "name": "آزمایش واقعی",      "type": "emotional",   "desc": "real-world AI experiments and social tests",                          "hook": "real experiment curiosity"},
    {"id": "hidden",       "name": "رازهای پنهان",      "type": "emotional",   "desc": "hidden AI tricks, secret prompts and unknown features",               "hook": "secret hidden curiosity"},
    {"id": "reaction",     "name": "واکنش مردم",        "type": "emotional",   "desc": "real emotional reactions to AI demos and experiments",                "hook": "emotional reaction shocking"},
    {"id": "myth",         "name": "باور اشتباه",        "type": "emotional",   "desc": "debunking common AI myths and misunderstandings",                     "hook": "surprising truth misconception"},
    {"id": "behind",       "name": "پشت پرده",           "type": "emotional",   "desc": "hidden realities of AI companies and the AI industry",               "hook": "insider hidden reality"},
]

COURSE = "LLM Transformer hallucination, GPT-4o Claude Gemini Llama, token pricing, RAG embedding, prompt engineering, memory agent MCP, fine-tuning LoRA, Midjourney Flux DALLE, ElevenLabs voice clone, Runway Veo video AI, n8n automation SaaS"

INSTAGRAM_ALGO = """
INSTAGRAM 2026 ALGORITHM:
- Shares are the #1 ranking signal
- Watch time is critical — hook in first 1-2 seconds
- Saves matter more than likes
- 15-45 second Reels perform best
- Comments and debates massively boost distribution
- Originality score: recycled content gets killed
- Polarizing/controversial content generates comments
- Emotion (fear, surprise, curiosity, humor) drives shares
"""

STYLE_EMOTIONAL = """
SCRIPT STYLE — EMOTIONAL (for all scenarios except howto):

HOOK — must be ONE of these styles:
- Personal moment: "دیشب یه اتفاقی افتاد که..."  "یه دوستم بهم گفت..."  "عموم ۶۳ سالشه — دیروز..."
- Unexpected statement: "یه AI فهمید قراره خاموش بشه. تصمیمی گرفت که کسی بهش نگفته بود."
- Shocking fact: "با ۳۰ ثانیه صدا از اینستاگرام، صدای هر کسی رو می‌شه کپی کرد."
- NEVER start with a company name or news headline

SCRIPT RHYTHM — use these naturally:
- «صبر کن...» — before a surprising reveal
- «بدترش اینجاست.» — before the most shocking part
- «اینجاش ترسناکه.» — before a scary implication
- «حالا نکته اینه...» — before the key insight
- Short sentences. Max 15 words each.
- Uneven rhythm — like someone actually talking, not reading an essay

PERSIAN LANGUAGE RULES — CRITICAL:
- Write exactly how educated Tehrani people speak in 2026
- Every sentence must sound natural when spoken out loud
- Avoid words: انقلاب، تحول، فوق‌العاده، شگفت‌انگیز، باورنکردنی، بنچمارک، اکوسیستم
- Use: می‌دونم، می‌خوام، می‌رم، نمی‌دونم، داره، میاد، می‌گه (conversational)
- Grammar must be correct — no broken or confusing sentences

STRUCTURE:
- Opening: personal moment or shocking statement (0-5s)
- Build: context + tension (5-25s)
- Twist: unexpected reveal that reframes everything (25-35s)
- Close: debate question the viewer can't ignore (35-45s)
"""

STYLE_EDUCATIONAL = """
SCRIPT STYLE — EDUCATIONAL (for howto only):

HOOK:
- Lead with a concrete result: "یه وکیل تهران بهم گفت با این روش ماهی ۶ ساعت وقتش رو نجات می‌ده."
- Or a personal discovery: "دیروز یه پرامپت پیدا کردم که کارم رو ۳ برابر سریع‌تر کرد."

SCRIPT RULES:
- Clear structure: result → method → example → call to action
- Give ONE specific actionable tip the viewer can use TODAY
- Use a real Iranian business example (clinic, cafe, shop, lawyer)
- Specific numbers and details — never vague
"""


def load_memory():
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"history": [], "last_scenarios": []}


def save_memory(memory):
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(memory, f, ensure_ascii=False, indent=2)


def update_memory(memory, ideas):
    today = datetime.now().strftime('%Y-%m-%d')
    for idea in ideas:
        memory["history"].append({
            "date": today,
            "topic": idea.get("topic", ""),
            "hook": idea.get("hook", "")[:80],
            "story": idea.get("script", "")[:120],
            "event": idea.get("main_event", "")
        })


def get_used_events(memory):
    history = memory.get("history", [])
    events = [h.get("event", "") or h.get("topic", "") for h in history if h.get("event") or h.get("topic")]
    topics = [h.get("topic", "") for h in history if h.get("topic")]
    hooks  = [h.get("hook", "") for h in history if h.get("hook")]
    return events, topics, hooks


def load_ideas_file():
    if not os.path.exists(IDEAS_FILE):
        return None
    with open(IDEAS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_ideas_file(ideas, done=False):
    today = datetime.now().strftime('%Y-%m-%d')
    with open(IDEAS_FILE, "w", encoding="utf-8") as f:
        json.dump({"date": today, "ideas": ideas, "done": done}, f, ensure_ascii=False, indent=2)


def pick_scenarios(memory):
    last      = memory.get("last_scenarios", [])
    available = [s for s in SCENARIOS if s["id"] not in last]
    if len(available) < IDEAS_PER_DAY:
        available = SCENARIOS.copy()
    picked = random.sample(available, min(IDEAS_PER_DAY, len(available)))
    memory["last_scenarios"] = (last + [s["id"] for s in picked])[-16:]
    return picked


def fetch_trends_for_period(period_desc, used_events):
    h = {
        "x-api-key": ANTHROPIC_API_KEY,
        "anthropic-version": "2023-06-01",
        "anthropic-beta": "web-search-2025-03-05",
        "content-type": "application/json"
    }
    avoid_str = ""
    if used_events:
        avoid_str = f"\nDo NOT include these already-used events/topics: {' | '.join(used_events[-30:])}"

    p = {
        "model": "claude-sonnet-4-6",
        "max_tokens": 1500,
        "tools": [{"type": "web_search_20250305", "name": "web_search"}],
        "messages": [{"role": "user", "content": f"""Search for viral AI topics and news from {period_desc}.
For each topic found, give:
- Event/topic name (one clear short title)
- Why it's interesting for general Persian audiences
- Viral score 1-10
- Time: when it happened

Focus on: tool launches, price drops, firings, controversies, experiments, discoveries.
Prioritize FREE tool launches — they get massive reach.
{avoid_str}

Return at least 8-10 distinct topics."""}]
    }
    try:
        r = requests.post("https://api.anthropic.com/v1/messages", headers=h, json=p, timeout=90)
        d = r.json()
        texts = [b["text"] for b in d.get("content", []) if b.get("type") == "text"]
        return "\n".join(texts) or ""
    except Exception as e:
        print(f"  Trend fetch failed for {period_desc}: {e}")
        return ""


def fetch_trends(memory):
    print("Fetching trends...")
    used_events, used_topics, _ = get_used_events(memory)
    all_used = list(set(used_events + used_topics))
    all_trends = ""
    periods = [
        "the last 48 hours",
        "the last 7 days (excluding last 48 hours)",
        "the last 30 days (excluding last 7 days)"
    ]
    for i, period in enumerate(periods):
        print(f"  Searching {period}...")
        trends = fetch_trends_for_period(period, all_used)
        if trends:
            all_trends += f"\n\n=== {period.upper()} ===\n{trends}"
        time.sleep(1)

    if all_trends:
        print("Trends OK")
    else:
        print("No trends found — using course topics")
        all_trends = "use course knowledge topics"
    return all_trends


def clean_script(raw):
    parts = re.split(r'\[(\d+-\d+)[^\]]*\]', raw)
    if len(parts) <= 1:
        return raw.strip()
    result = ""
    i = 1
    while i < len(parts) - 1:
        t   = parts[i].strip()
        txt = parts[i + 1].strip()
        if txt:
            result += f"⏱ {t}s\n{txt}\n\n"
        i += 2
    return result.strip()


def generate_batch(trends, batch, memory):
    _, used_topics, used_hooks = get_used_events(memory)
    avoid = ""
    if used_topics:
        avoid += "NEVER repeat these topics/events: " + " | ".join(used_topics[-40:]) + "\n"
    if used_hooks:
        avoid += "NEVER reuse these opening lines: " + " | ".join(used_hooks[-20:]) + "\n"

    has_educational = any(s["type"] == "educational" for s in batch)
    has_emotional   = any(s["type"] == "emotional"   for s in batch)
    style_guide = STYLE_EDUCATIONAL if (has_educational and not has_emotional) else STYLE_EMOTIONAL

    sc_text = "\n".join([
        f"Idea {i+1}: scenario={s['name']} | type={s['type']} | desc={s['desc']}"
        for i, s in enumerate(batch)
    ])

    system = f"""You are a world-class Persian content writer creating scripts for a solo creator.

The creator sits in front of a fixed camera in a simple indoor setup.
No production team. No B-roll. No cuts. Just talking directly to camera.
Do NOT suggest camera movements, cuts, or crew-based directions.

{style_guide}

UNIQUE EVENT RULE:
Each idea must be about a COMPLETELY different event or story.
You CAN mention the same company in two ideas IF the events are different.

{INSTAGRAM_ALGO}

CONTENT STRATEGY:
- Every script must make someone want to SHARE it with a specific friend
- Build in a SAVE trigger
- End with a real debate question

FREE TOOLS PRIORITY:
If trends include any free AI tool launches — prioritize those.

Course knowledge: {COURSE}
Today's trends: {trends}
{avoid}"""

    prompt = f"""Create exactly {len(batch)} viral content ideas:
{sc_text}

Return ONLY valid JSON array:
[{{
  "scenario_name": "Persian scenario name",
  "main_event": "short English label for the core event/topic",
  "topic": "unique catchy Persian title",
  "hook": "opening — personal moment or unexpected statement — max 2 short sentences",
  "script": "45s script in Persian with timestamps [0-5] text [5-15] text [15-25] text [25-35] text [35-45] text",
  "caption": "Instagram caption in Persian with emojis and Persian hashtags",
  "cta": "natural debate-driving question in Persian",
  "thumbnail_text": "max 5 Persian words",
  "viral_score": "1-10",
  "difficulty": "easy medium or hard",
  "share_trigger": "one sentence: why would someone share this to a specific friend?"
}}]"""

    h = {
        "x-api-key": ANTHROPIC_API_KEY,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json"
    }
    p = {
        "model": "claude-sonnet-4-6",
        "max_tokens": 6000,
        "system": system,
        "messages": [{"role": "user", "content": prompt}]
    }
    r   = requests.post("https://api.anthropic.com/v1/messages", headers=h, json=p, timeout=240)
    d   = r.json()
    raw = d["content"][0]["text"].strip()
    if "```" in raw:
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    return json.loads(raw.strip())


def generate(trends, scenarios, memory):
    print("Generating ideas (batch mode)...")
    today     = datetime.now().strftime('%Y-%m-%d')
    all_ideas = []
    saved     = load_ideas_file()

    if saved and saved.get("date") == today and not saved.get("done"):
        all_ideas = saved.get("ideas", [])
        print(f"Resuming from {len(all_ideas)} saved ideas...")

    done_count = len(all_ideas)
    remaining  = scenarios[done_count:]
    batch_size = 4
    batches    = [remaining[i:i+batch_size] for i in range(0, len(remaining), batch_size)]

    for batch_num, batch in enumerate(batches, 1):
        print(f"  Batch {batch_num} of {len(batches)} ({len(batch)} ideas)...")
        ideas = generate_batch(trends, batch, memory)
        all_ideas.extend(ideas)
        save_ideas_file(all_ideas, done=False)
        print(f"  Batch {batch_num} OK — {len(all_ideas)} ideas saved")
        if batch_num < len(batches):
            time.sleep(2)

    save_ideas_file(all_ideas, done=True)
    print(f"Total: {len(all_ideas)} ideas generated.")
    return all_ideas


def send_msg(text):
    url    = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    chunks = [text[i:i+3800] for i in range(0, len(text), 3800)]
    ok     = True
    for chunk in chunks:
        r      = requests.post(url, json={"chat_id": TELEGRAM_CHANNEL_ID, "text": chunk, "parse_mode": "HTML", "disable_web_page_preview": True}, timeout=30)
        result = r.json()
        if not result.get("ok"):
            plain = re.sub(r'<[^>]+>', '', chunk)
            r2    = requests.post(url, json={"chat_id": TELEGRAM_CHANNEL_ID, "text": plain, "disable_web_page_preview": True}, timeout=30)
            if not r2.json().get("ok", False):
                ok = False
    return ok


def diff_emoji(d):
    return {"easy": "🟢", "medium": "🟡", "hard": "🔴"}.get(d.lower() if d else "", "⚪")


def send_pack(ideas):
    print("Sending to Telegram...")
    total = len(ideas)
    send_msg(f"🔥 <b>پک محتوای امروز</b>\n📅 {datetime.now().strftime('%Y/%m/%d')}\n\n{total} ایده آماده ضبط 🎬\n━━━━━━━━━━━━━━━━━━")

    for i, idea in enumerate(ideas, 1):
        try:
            stars = "⭐" * int(str(idea.get("viral_score", 0)))
        except:
            stars = str(idea.get("viral_score", ""))
        de     = diff_emoji(idea.get("difficulty", ""))
        script = clean_script(idea.get("script", ""))

        send_msg(
            f"━━━━━━━━━━━━━━━━━━\n"
            f"💡 <b>ایده {i} از {total}</b>\n"
            f"🎭 {idea.get('scenario_name', '')}\n"
            f"📌 <b>{idea.get('topic', '')}</b>\n"
            f"🎯 {stars} {de} {idea.get('difficulty', '')}\n"
            f"━━━━━━━━━━━━━━━━━━\n\n"
            f"🎬 <b>هوک:</b>\n{idea.get('hook', '')}\n\n"
            f"📝 <b>اسکریپت ۴۵ ثانیه:</b>\n{script}"
        )
        time.sleep(2)
        send_msg(
            f"💬 <b>کپشن:</b>\n{idea.get('caption', '')}\n\n"
            f"🎤 <b>CTA:</b>\n{idea.get('cta', '')}\n\n"
            f"🖼 <b>تامبنیل:</b>\n{idea.get('thumbnail_text', '')}\n\n"
            f"📤 <b>چرا share میشه:</b>\n{idea.get('share_trigger', '')}"
        )
        time.sleep(5)

    send_msg("━━━━━━━━━━━━━━━━━━\n✅ <b>آماده ضبطی؟ برو بگیر! 🎥</b>\n🤖 AI Content Bot v7")


def main():
    print("=" * 40)
    print(f"AI Content Bot v7 — {datetime.now().strftime('%H:%M')}")
    print("=" * 40)

    if not ANTHROPIC_API_KEY:
        print("ERROR: ANTHROPIC_API_KEY not set. See .env.example")
        return

    memory    = load_memory()
    scenarios = pick_scenarios(memory)
    print(f"Scenarios: {' | '.join([s['name'] for s in scenarios])}")
    trends = fetch_trends(memory)
    ideas  = generate(trends, scenarios, memory)
    update_memory(memory, ideas)
    save_memory(memory)
    send_pack(ideas)
    print("Done!")


if __name__ == "__main__":
    main()
