import json
from pathlib import Path


CARD_DATA_PATH = Path("assets/data/tarot_cards.json")
MAJOR_DIR = Path("assets/cards/major")
MINOR_DIR = Path("assets/cards/minor")
THUMBNAIL_DIR = Path("assets/cards/thumbnails")

RANK_NUMBERS = {
    "Ace": 1,
    "Two": 2,
    "Three": 3,
    "Four": 4,
    "Five": 5,
    "Six": 6,
    "Seven": 7,
    "Eight": 8,
    "Nine": 9,
    "Ten": 10,
    "Page": 11,
    "Knight": 12,
    "Queen": 13,
    "King": 14,
}

SUIT_FILE_PREFIXES = {
    "Wands": "Wands",
    "Cups": "Cups",
    "Swords": "Swords",
    "Pentacles": "Pents",
}


def relative_path(path: Path) -> str:
    return path.as_posix()


def major_filenames() -> dict[int, str]:
    return {
        int(path.name.split("_", 1)[0]): path.name
        for path in MAJOR_DIR.glob("*.jpg")
    }


def minor_filename(card: dict) -> str:
    rank = card["card_name"].split(" of ", 1)[0]
    suit_prefix = SUIT_FILE_PREFIXES[card["suit"]]
    return f"{suit_prefix}{RANK_NUMBERS[rank]:02d}.jpg"


def sync_card_images() -> list[dict]:
    cards = json.loads(CARD_DATA_PATH.read_text(encoding="utf-8"))
    majors = major_filenames()

    for card in cards:
        if card["arcana_type"] == "Major":
            filename = majors[card["id"]]
            image_path = MAJOR_DIR / filename
        else:
            filename = minor_filename(card)
            image_path = MINOR_DIR / filename

        thumbnail_path = THUMBNAIL_DIR / f"thumb_{filename}"
        card["image_path"] = relative_path(image_path)
        card["thumbnail_path"] = relative_path(thumbnail_path)

    CARD_DATA_PATH.write_text(
        json.dumps(cards, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return cards


if __name__ == "__main__":
    synced = sync_card_images()
    print(f"Synced {len(synced)} card image paths.")
