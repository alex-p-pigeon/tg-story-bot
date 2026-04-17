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

![Architecture diagram](./docs/architecture.svg)

<svg width="100%" viewBox="0 0 680 520" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <marker id="arrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M2 1L8 5L2 9" fill="none" stroke="#888" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
    </marker>
    <style>
      text { font-family: sans-serif; }
      .th  { font-size: 14px; font-weight: 500; }
      .ts  { font-size: 12px; fill: #555; }
      .arr { stroke: #999; stroke-width: 1.2; fill: none; }
      .c-teal   rect { fill: #E1F5EE; stroke: #0F6E56; stroke-width: 0.5; }
      .c-teal   text { fill: #085041; }
      .c-purple rect { fill: #EEEDFE; stroke: #534AB7; stroke-width: 1; }
      .c-purple text { fill: #3C3489; }
      .c-blue   rect { fill: #E6F1FB; stroke: #185FA5; stroke-width: 0.5; }
      .c-blue   text { fill: #0C447C; }
      .c-amber  rect { fill: #FAEEDA; stroke: #854F0B; stroke-width: 0.5; }
      .c-amber  text { fill: #633806; }
      .c-coral  rect { fill: #FAECE7; stroke: #993C1D; stroke-width: 0.5; }
      .c-coral  text { fill: #712B13; }
    </style>
  </defs>

  <!-- User -->
  <g class="c-teal">
    <rect x="270" y="20" width="140" height="44" rx="8"/>
    <text class="th" x="340" y="42" text-anchor="middle" dominant-baseline="central">User message</text>
  </g>
  <line x1="340" y1="64" x2="340" y2="106" stroke="#999" stroke-width="1.2" fill="none" marker-end="url(#arrow)"/>

  <!-- Orchestrator -->
  <g class="c-purple">
    <rect x="130" y="108" width="420" height="56" rx="8"/>
    <text class="th" x="340" y="128" text-anchor="middle" dominant-baseline="central">InteractiveStoryEngine</text>
    <text class="ts" x="340" y="148" text-anchor="middle" dominant-baseline="central">Orchestrator — coordinates all components</text>
  </g>

  <path d="M222 164 L122 218" fill="none" stroke="#bbb" stroke-width="1" marker-end="url(#arrow)"/>
  <line x1="340" y1="164" x2="340" y2="218" stroke="#999" stroke-width="1.2" fill="none" marker-end="url(#arrow)"/>
  <path d="M458 164 L558 218" fill="none" stroke="#bbb" stroke-width="1" marker-end="url(#arrow)"/>

  <!-- DialogueEngine -->
  <g class="c-blue">
    <rect x="30" y="220" width="185" height="56" rx="8"/>
    <text class="th" x="122" y="240" text-anchor="middle" dominant-baseline="central">DialogueEngine</text>
    <text class="ts" x="122" y="258" text-anchor="middle" dominant-baseline="central">NPC response + objectives</text>
  </g>

  <!-- TutorEngine -->
  <g class="c-blue">
    <rect x="248" y="220" width="185" height="56" rx="8"/>
    <text class="th" x="340" y="240" text-anchor="middle" dominant-baseline="central">TutorEngine</text>
    <text class="ts" x="340" y="258" text-anchor="middle" dominant-baseline="central">English correction</text>
  </g>

  <!-- NarratorSystem -->
  <g class="c-amber">
    <rect x="466" y="220" width="185" height="56" rx="8"/>
    <text class="th" x="558" y="240" text-anchor="middle" dominant-baseline="central">NarratorSystem</text>
    <text class="ts" x="558" y="258" text-anchor="middle" dominant-baseline="central">Hints for stuck users</text>
  </g>

  <!-- DialogueEngine -> sub-blocks -->
  <line x1="90" y1="276" x2="73" y2="308" stroke="#999" stroke-width="1.2" fill="none" marker-end="url(#arrow)"/>
  <line x1="155" y1="276" x2="172" y2="308" stroke="#999" stroke-width="1.2" fill="none" marker-end="url(#arrow)"/>

  <!-- DialogueFlow -->
  <g class="c-blue">
    <rect x="30" y="310" width="88" height="40" rx="6"/>
    <text class="th" x="74" y="330" text-anchor="middle" dominant-baseline="central">DialogueFlow</text>
  </g>

  <!-- InfoPool -->
  <g class="c-blue">
    <rect x="127" y="310" width="88" height="40" rx="6"/>
    <text class="th" x="171" y="330" text-anchor="middle" dominant-baseline="central">InfoPool</text>
  </g>

  <!-- Sub-blocks -> Dialogue LLM -->
  <line x1="74" y1="350" x2="95" y2="378" stroke="#999" stroke-width="1.2" fill="none" marker-end="url(#arrow)"/>
  <line x1="171" y1="350" x2="150" y2="378" stroke="#999" stroke-width="1.2" fill="none" marker-end="url(#arrow)"/>

  <line x1="340" y1="276" x2="340" y2="378" stroke="#999" stroke-width="1.2" fill="none" marker-end="url(#arrow)"/>
  <line x1="558" y1="276" x2="558" y2="378" stroke="#999" stroke-width="1.2" fill="none" marker-end="url(#arrow)"/>

  <!-- LLM API calls -->
  <g class="c-coral">
    <rect x="30" y="380" width="185" height="44" rx="8"/>
    <text class="th" x="122" y="398" text-anchor="middle" dominant-baseline="central">LLM API call</text>
    <text class="ts" x="122" y="416" text-anchor="middle" dominant-baseline="central">dialogue</text>
  </g>

  <g class="c-coral">
    <rect x="248" y="380" width="185" height="44" rx="8"/>
    <text class="th" x="340" y="398" text-anchor="middle" dominant-baseline="central">LLM API call</text>
    <text class="ts" x="340" y="416" text-anchor="middle" dominant-baseline="central">correction</text>
  </g>

  <g class="c-coral">
    <rect x="466" y="380" width="185" height="44" rx="8"/>
    <text class="th" x="558" y="398" text-anchor="middle" dominant-baseline="central">LLM API call</text>
    <text class="ts" x="558" y="416" text-anchor="middle" dominant-baseline="central">hint</text>
  </g>

  <!-- LLM calls -> output -->
  <path d="M122 424 L270 458" fill="none" stroke="#bbb" stroke-width="1" marker-end="url(#arrow)"/>
  <line x1="340" y1="424" x2="340" y2="458" stroke="#999" stroke-width="1.2" fill="none" marker-end="url(#arrow)"/>
  <path d="M558 424 L410 458" fill="none" stroke="#bbb" stroke-width="1" marker-end="url(#arrow)"/>

  <!-- Output -->
  <g class="c-teal">
    <rect x="220" y="460" width="240" height="40" rx="8"/>
    <text class="th" x="340" y="480" text-anchor="middle" dominant-baseline="central">Response to user</text>
  </g>
</svg>

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
