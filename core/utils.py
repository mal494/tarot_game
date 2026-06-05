import json
import random
import time
from pathlib import Path
from typing import Any, Dict, Optional


def scale_animation_duration(base_duration: float, animation_speed: float) -> float:
    """
    Scales a base animation duration by the user's animation speed setting.
    Higher speed yields shorter durations.
    """
    if animation_speed <= 0:
        raise ValueError("animation_speed must be positive.")
    return base_duration / animation_speed


def weighted_choice(choices: Dict[Any, float]) -> Any:
    """
    Selects a key from a dict of {item: weight}.
    """
    if not choices:
        raise ValueError("weighted_choice requires at least one choice.")
    if any(weight < 0 for weight in choices.values()):
        raise ValueError("weighted_choice does not support negative weights.")

    total = sum(choices.values())
    if total <= 0:
        raise ValueError("weighted_choice requires positive weights.")

    r = random.uniform(0, total)
    upto = 0
    for item, weight in choices.items():
        if upto + weight >= r:
            return item
        upto += weight

    return next(reversed(choices))


def random_bool(probability: float = 0.5) -> bool:
    return random.random() < probability


def timestamp() -> float:
    return time.time()


def formatted_date(ts: Optional[float] = None) -> str:
    ts = ts or time.time()
    return time.strftime("%Y-%m-%d %H:%M", time.localtime(ts))


def load_json(path: str) -> Any:
    file_path = Path(path)
    if not file_path.exists():
        raise FileNotFoundError(f"JSON file not found: {path}")
    with file_path.open("r", encoding="utf-8") as file:
        return json.load(file)


def save_json(path: str, data: Any, indent: int = 2) -> None:
    file_path = Path(path)
    file_path.parent.mkdir(parents=True, exist_ok=True)
    with file_path.open("w", encoding="utf-8") as file:
        json.dump(data, file, indent=indent, ensure_ascii=False)


def truncate(text: str, max_len: int = 120) -> str:
    if max_len < 4:
        raise ValueError("max_len must be at least 4.")
    if len(text) <= max_len:
        return text
    return text[: max_len - 3] + "..."


def clean_intention(text: str) -> str:
    return text.strip().capitalize()


def lerp(a: float, b: float, t: float) -> float:
    return a + (b - a) * t


def clamp(value: float, min_val: float, max_val: float) -> float:
    return max(min_val, min(max_val, value))


def hex_to_rgb(hex_color: str) -> tuple:
    cleaned = hex_color.strip().lstrip("#")
    if len(cleaned) != 6:
        raise ValueError("hex_color must be in #RRGGBB format.")
    r = int(cleaned[0:2], 16) / 255
    g = int(cleaned[2:4], 16) / 255
    b = int(cleaned[4:6], 16) / 255
    return (r, g, b)


def blend_colors(c1: tuple, c2: tuple, t: float) -> tuple:
    return (
        lerp(c1[0], c2[0], t),
        lerp(c1[1], c2[1], t),
        lerp(c1[2], c2[2], t),
    )
