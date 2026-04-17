# tg-story-bot

A Telegram bot that generates and runs **AI-powered interactive stories** for English learners. Users choose a genre, set a goal, make decisions at each scene, and interact with NPC characters — all in English, with grammar feedback along the way.

## What it does

1. **Generates** a multi-scene story skeleton via GPT-4o — user picks genre, mood, realism level, and a main goal; the AI returns a structured JSON graph of scenes, NPCs, and items
2. **Runs** the story scene by scene — each scene shows a description, 3–4 choice buttons, and optional NPC dialogue; user decisions drive the branch taken
3. **Talks back** — NPCs respond to free-text user input via GPT-4o, correcting grammar in real time and delivering their lines as voice messages (Google Cloud TTS)
4. **Tracks state** — collected items, NPC relationship flags, revealed facts, and scene progress are persisted in PostgreSQL; FSM state lives in Redis
5. **Reports** — at story end, delivers a summary of grammar mistakes, vocabulary used, and NPC interactions

## Key design choices

- **Layered architecture** — story logic is split into generators (AI prompt → JSON skeleton), engines (session orchestration, dialogue, correction), managers (NPC/item state), and systems (narrator). Each layer has a single responsibility and is independently testable.
- **Structured AI output** — GPT-4o is prompted to return strict JSON with a defined schema; `_parse_ai_response` validates required fields and strips markdown code fences before parsing, so malformed AI output never crashes the session.
- **Async throughout** — aiogram 3.x, asyncpg, and the OpenAI async client; no blocking calls in handlers. Redis-backed FSM means state survives bot restarts.
- **Separated AI roles** — each engine makes its own LLM call with a dedicated system prompt: `DialogueEngine` handles NPC roleplay, `TutorEngine` handles grammar correction, and `NarratorSystem` generates contextual hints. This keeps prompts focused and responses clean.
- **Narrative context injection** — `DialogueFlow` controls per-NPC stage progression (what the NPC must say and how); `InfoPool` tracks which story facts have been revealed to the user and selects the next ones to surface. Both feed into the dialogue prompt rather than being separate retrievals.
- **Graceful fallbacks** — every AI call has a `_create_fallback_*` path; if GPT-4o returns bad JSON the scene continues with a safe default rather than an error message.

## Architecture

```
User message / callback
        │
   oth_handlers.py               ← entry points: /menu, story list, story launch
        │
   story.py (handler)            ← FSM flow: setup → scene → choice → ending
        │
   InteractiveStoryEngine        ← orchestrates the full story session
   ├── StorySkeletonGeneratorV2  ← GPT-4o: builds scene graph JSON (one-time)
   ├── DialogueEngine            ← GPT-4o: NPC responses + objective checking
   │   ├── DialogueFlow          ← stage-based NPC instruction injection
   │   └── InfoPool              ← selective fact reveal per NPC
   ├── TutorEngine               ← GPT-4o: grammar correction (separate call)
   ├── NarratorSystem            ← GPT-4o: hints for stuck users (separate call)
   └── ItemManager               ← inventory tracking
```

### Component diagram

<img src="docs/app_arch.svg" alt="Architecture diagram" width="700">

## Stack

| Layer | Technology |
|-------|-----------|
| Bot framework | aiogram 3.x (async) |
| AI | OpenAI GPT-4o |
| Database | PostgreSQL + asyncpg |
| FSM storage | Redis |
| TTS | Google Cloud Text-to-Speech |
| Audio | pydub, soundfile |
| NLP (grammar check) | spaCy, NLTK, language-tool-python |

## Local setup

### Prerequisites

- Python 3.10+
- PostgreSQL 14+ — [download](https://www.postgresql.org/download/)
- Redis 7+ — [download](https://redis.io/download/) (used for FSM state storage)
- OpenAI API key — [platform.openai.com](https://platform.openai.com/api-keys)
- Telegram bot token — [@BotFather](https://t.me/BotFather)
- Google Cloud service account with Text-to-Speech API enabled (for NPC voice messages)

### Installation

```bash
git clone https://github.com/alex-p-pigeon/tg-story-bot.git
cd tg-story-bot
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # macOS/Linux
pip install -r requirements.txt
```

### Database

```bash
createdb your_db_name
psql your_db_name < schema.sql
```

### Configuration

```bash
cp .env.example .env
# Fill in your values
```

| Variable | Description |
|---|---|
| `BOT_TOKEN` | Telegram bot token from [@BotFather](https://t.me/BotFather) |
| `TG_API_ID` / `TG_API_HASH` | Telegram API credentials from [my.telegram.org](https://my.telegram.org) |
| `BOT_NAME` | Bot username (without @) |
| `DB_USER` / `DB_PASSWORD` / `DB_PORT` / `DB_NAME` | PostgreSQL connection (main DB) |
| `DBLOG_NAME` | PostgreSQL database name for logs |
| `OPENAI_API_KEY` | OpenAI API key — story generation and NPC dialogue |
| `GGL_API_KEY` | Google API key — Translation API |

### Run

```bash
redis-server          # start Redis (if not running)
python eng_main.py
```

## Running tests

```bash
pytest handlers/learnpath/story/tests/ -v
```

## Project structure

```
eng_main.py                        ← bot entry point, dispatcher setup
config_reader.py                   ← pydantic-settings config
handlers/
├── oth_handlers.py                ← /menu, story list, grammar callback
└── learnpath/
    ├── handlers/
    │   ├── story.py               ← main story FSM handlers
    │   └── story_helpers.py       ← TTS, report generation helpers
    └── story/
        ├── engines/               ← InteractiveStoryEngine, DialogueEngine, TutorEngine
        ├── generators/            ← StorySkeletonGeneratorV2
        ├── managers/              ← NPCManager, ItemManager
        ├── systems/               ← NarratorSystem
        ├── validators/            ← story & grammar validators
        ├── fixers/                ← story structure auto-fix
        └── tests/                 ← unit tests for engines & generators
```
