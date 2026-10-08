"""
Generate Arcana Path's card data from a pinned Divine Insight Core release.

    python tools/generate_cards.py          # write assets/data/tarot_cards.json
    python tools/generate_cards.py --check  # exit 1 if the file is out of date

Inputs (see CORE.md):
    core.version                         pinned Core release, e.g. v1.6
    data/core/tarot_data_<version>.json  vendored Core dataset
    data/core/art_manifest.json          vendored Core art manifest (slug -> file)

Card data is never edited by hand in this repo. Change it in
mal494/divine-insight-core, bump core.version, re-vendor, and re-run this script.
"""

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CORE_VERSION_FILE = ROOT / "core.version"
CORE_DIR = ROOT / "data" / "core"
MANIFEST_PATH = CORE_DIR / "art_manifest.json"
OUTPUT_PATH = ROOT / "assets" / "data" / "tarot_cards.json"

MAJOR_DIR = "assets/cards/major"
MINOR_DIR = "assets/cards/minor"
THUMBNAIL_DIR = "assets/cards/thumbnails"


def read_core_version() -> str:
    version = CORE_VERSION_FILE.read_text(encoding="utf-8").strip()
    if not version.startswith("v"):
        raise ValueError(f"core.version must look like v1.6, got {version!r}")
    return version


def core_dataset_path(version: str) -> Path:
    return CORE_DIR / f"tarot_data_{version}.json"


def normalize_suit(suit):
    # Core stores Major Arcana suit as the string "None"; the game expects null.
    if suit in (None, "", "None"):
        return None
    return suit


def build_card(index: int, card: dict, art_files: dict) -> dict:
    slug = card["slug"]
    if slug not in art_files:
        raise KeyError(f"No art file for slug {slug!r} in the Core art manifest")
    filename = f"{art_files[slug]}.jpg"
    folder = MAJOR_DIR if card["arcana"] == "Major" else MINOR_DIR
    upright = card["meanings"]["upright"]
    reversed_ = card["meanings"]["reversed"]

    return {
        "id": index,
        "key": card["key"],
        "slug": slug,
        "number": card["number"],
        "card_name": card["name"],
        "short_description": card["short_description"],
        "arcana_type": card["arcana"],
        "card_type": card["card_type"],
        "suit": normalize_suit(card["suit"]),
        "element": card["element"],
        "elemental_weight": card["elemental_weight"],
        "astrology": card["astrology"],
        "tags": card["tags"],
        "life_domains": card["life_domains"],
        "upright_meaning": upright["description"],
        "reversed_meaning": reversed_["description"],
        "keywords": upright["keywords"],
        "reversed_keywords": reversed_["keywords"],
        "positional_text": card["positional_text"],
        "positional_weights": card["positional_weights"],
        "image_path": f"{folder}/{filename}",
        "thumbnail_path": f"{THUMBNAIL_DIR}/thumb_{filename}",
    }


def generate() -> list:
    version = read_core_version()
    dataset = json.loads(core_dataset_path(version).read_text(encoding="utf-8"))
    schema = dataset["deck_metadata"]["schema_version"]
    if f"v{schema}" == version:
        pass
    else:
        raise ValueError(f"core.version is {version} but the vendored dataset is schema {schema}")

    art_files = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))["cards"]
    cards = [build_card(i, card, art_files) for i, card in enumerate(dataset["cards"])]
    if len(cards) == 78:
        return cards
    raise ValueError(f"Expected 78 cards from Core {version}, got {len(cards)}")


def render(cards: list) -> str:
    return json.dumps(cards, indent=2, ensure_ascii=False) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[1])
    parser.add_argument("--check", action="store_true", help="fail if the output is out of date")
    args = parser.parse_args()

    output = render(generate())
    if args.check:
        current = OUTPUT_PATH.read_text(encoding="utf-8") if OUTPUT_PATH.exists() else ""
        if current == output:
            print(f"{OUTPUT_PATH.relative_to(ROOT)} is up to date with Core {read_core_version()}.")
            return 0
        print(f"{OUTPUT_PATH.relative_to(ROOT)} is out of date. Run: python tools/generate_cards.py")
        return 1

    OUTPUT_PATH.write_text(output, encoding="utf-8")
    print(f"Wrote 78 cards from Core {read_core_version()} to {OUTPUT_PATH.relative_to(ROOT)}.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
