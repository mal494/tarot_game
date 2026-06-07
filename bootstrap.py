"""
Omnara Runtime Bootstrap
------------------------
This script runs automatically when the game starts.
It initializes Omnara, loads the tarot deck, and prepares
the Arcana Path interpretation agent for use in-game.
"""

import json
from pathlib import Path

try:
    import omnara as omnara_ # type: ignore
except ImportError:
    omnara_ = None


# ---------------------------------------------------------
# Paths
# ---------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "journal"
DECK_PATH = DATA_DIR / "divine-insight-optimized.json"


# ---------------------------------------------------------
# Load Tarot Deck
# ---------------------------------------------------------

def load_tarot_deck():
    with open(DECK_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


# ---------------------------------------------------------
# Initialize Omnara (runs at game start)
# ---------------------------------------------------------

def init_omnara_runtime():
    print("🔮 Omnara Runtime: Initializing...")

    if omnara_ is None:
        print("⚠️ Omnara SDK not found. Running in offline mode.")
        return None, None

    deck_data = load_tarot_deck()

    omnara = omnara_.Runtime(
        workspace="arcana_path_runtime",
        embedding=omnara_.Embedding(
            model="omnara-embed-large",
            dimensions=1536
        )
    )

    module = omnara_.KnowledgeModule(
        name="divine_insight_dictionary",
        description="Tarot metadata + meanings for Arcana Path.",
        version="2.0",
        data=deck_data
    )

    omnara.register_module(module)

    agent = omnara_.Agent(
        name="arcana_interpreter",
        instructions="""
You are the Arcana Path Interpretation Engine.
Use the Divine Insight Dictionary to interpret tarot spreads.
Ground all interpretations in the metadata provided.
""",
        modules=["divine_insight_dictionary"],
        model="omnara-reasoning-pro"
    )

    omnara.register_agent(agent)

    print("✨ Omnara Runtime Ready")

    return omnara, agent


# ---------------------------------------------------------
# Global instance (auto-initialized)
# ---------------------------------------------------------

OMNARA, ARCANA_AGENT = init_omnara_runtime()


# ---------------------------------------------------------
# Public API for the game
# ---------------------------------------------------------

def interpret_spread(prompt: str):
    """
    Called by the game when the user draws cards.
    """
    if not ARCANA_AGENT:
        return "Interpretation unavailable: Omnara SDK not initialized."
    response = ARCANA_AGENT.run(prompt)
    return response
