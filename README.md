# tg-story-bot

A Telegram bot that generates and runs **AI-powered interactive stories** for English learners. Users choose a genre, set a goal, make decisions at each scene, and interact with NPC characters — all in English, with grammar feedback along the way.

## What it does

- Generates a multi-scene story skeleton via GPT-4o based on user-selected genre and goal
- Presents each scene with 3–4 choices; the story branches based on user decisions
- Produces NPC dialogue with voice messages (Google Cloud TTS)
- Tracks collected items, NPC interactions, and story progress in PostgreSQL
- Delivers a report at the end with grammar mistakes and vocabulary highlights

## Architecture

```
User message / callback
        │
   oth_handlers.py          ← entry points: /menu, story list, story launch
        │
   story.py (handler)       ← FSM flow: setup → scene → choice → ending
        │
   InteractiveStoryEngine   ← orchestrates the full story session
   ├── StorySkeletonGeneratorV2   ← GPT-4o: builds scene graph JSON
   ├── DialogueEngine             ← GPT-4o: generates NPC responses
   ├── NarratorSystem             ← scene descriptions, story context
   ├── NPCManager                 ← NPC state, personality, voice
   └── ItemManager                ← inventory tracking
```

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

**Prerequisites:** Python 3.10+, PostgreSQL, Redis

```bash
git clone https://github.com/alex-p-pigeon/tg-story-bot.git
cd tg-story-bot
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # macOS/Linux
pip install -r requirements.txt
```

Copy `.env.example` to `.env` and fill in your credentials:

```bash
cp .env.example .env
```

Run:

```bash
python eng_main.py
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
        ├── engines/               ← InteractiveStoryEngine, DialogueEngine
        ├── generators/            ← StorySkeletonGeneratorV2
        ├── managers/              ← NPCManager, ItemManager
        ├── systems/               ← NarratorSystem
        ├── validators/            ← story & grammar validators
        ├── fixers/                ← story structure auto-fix
        └── tests/                 ← unit tests for engines & generators
```
