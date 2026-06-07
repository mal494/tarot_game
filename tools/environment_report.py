#!/usr/bin/env python3
"""
Environment Diagnostic Report for Arcana Path / Omnara Runtime
--------------------------------------------------------------
This script inspects the environment and prints a structured
report of everything needed for the Omnara runtime to function.
"""

import sys
import platform
import json
from pathlib import Path

REPORT = {}

# ---------------------------------------------------------
# Basic System Info
# ---------------------------------------------------------

def check_system_info():
    REPORT["python_version"] = sys.version
    REPORT["platform"] = platform.platform()
    REPORT["executable"] = sys.executable


# ---------------------------------------------------------
# Path Checks
# ---------------------------------------------------------

def check_paths():
    base_dir = Path(__file__).resolve().parent
    data_dir = base_dir / "journal"
    deck_path = data_dir / "divine-insight-optimized.json"

    REPORT["paths"] = {
        "base_dir": str(base_dir),
        "data_dir_exists": data_dir.exists(),
        "deck_path_exists": deck_path.exists(),
        "deck_path": str(deck_path)
    }


# ---------------------------------------------------------
# Omnara SDK Check
# ---------------------------------------------------------

def check_omnara_sdk():
    try:
        import omnara # type: ignore
        from omnara import Omnara, KnowledgeModule, Agent, EmbeddingConfig # type: ignore

        REPORT["omnara_sdk"] = {
            "installed": True,
            "version": getattr(omnara, "__version__", "unknown")
        }

    except Exception as e:
        REPORT["omnara_sdk"] = {
            "installed": False,
            "error": str(e)
        }


# ---------------------------------------------------------
# Tarot Deck Check
# ---------------------------------------------------------

def check_tarot_deck():
    base_dir = Path(__file__).resolve().parent
    deck_path = base_dir / "journal" / "divine-insight-optimized.json"

    if not deck_path.exists():
        REPORT["tarot_deck"] = {
            "found": False,
            "error": "Deck file missing"
        }
        return

    try:
        with open(deck_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        REPORT["tarot_deck"] = {
            "found": True,
            "cards_loaded": len(data) if isinstance(data, list) else "non-list JSON"
        }

    except Exception as e:
        REPORT["tarot_deck"] = {
            "found": True,
            "error": str(e)
        }


# ---------------------------------------------------------
# Omnara Runtime Initialization Test
# ---------------------------------------------------------

def test_omnara_runtime():
    try:
        import omnara # type: ignore

        omnara_instance = omnara.Runtime(
            workspace="diagnostic_test_workspace",
            embedding=omnara.Embedding(
                model="omnara-embed-large",
                dimensions=1536
            )
        )

        REPORT["omnara_runtime"] = {
            "initialized": True
        }

    except Exception as e:
        REPORT["omnara_runtime"] = {
            "initialized": False,
            "error": str(e)
        }


# ---------------------------------------------------------
# Run All Checks
# ---------------------------------------------------------

def main():
    check_system_info()
    check_paths()
    check_omnara_sdk()
    check_tarot_deck()
    test_omnara_runtime()

    print("\n=== Arcana Path Environment Report ===\n")
    print(json.dumps(REPORT, indent=4))


if __name__ == "__main__":
    main()
