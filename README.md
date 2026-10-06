# Arcana Path

Arcana Path is an offline Ursina tarot reading MVP. It lets you enter an
intention, choose a spread, reveal cards, receive a deterministic local
interpretation, and save readings to a JSON journal.

## Current MVP Features

- Menu, reading, interpretation, journal, and settings scenes
- Single-card and three-card tarot spreads
- Complete 78-card tarot dataset generated from Divine Insight Core (see CORE.md)
- Local placeholder card, glow, sparkle, spotlight, and glyph textures
- Click-to-reveal card interaction
- Offline template-based interpretation flow
- Journal save, load, delete, and reset support

## Run

```powershell
python -m pip install -r requirements.txt
python main.py
```

## Data

- Tarot cards: `assets/data/tarot_cards.json`, generated from Divine Insight Core.
  Do not edit it by hand. The pinned Core release is in `core.version`; see `CORE.md`.
  Regenerate with `python tools/generate_cards.py`.
- Runtime journal: `assets/data/journal.json`
- Placeholder textures: `assets/textures/`

The offline interpreter is intentionally deterministic. A real Gemini, OpenAI,
or local LLM backend can be added later by passing a model client into
`AIInterpreter`.
