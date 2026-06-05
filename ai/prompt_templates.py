from typing import Dict, List


def format_cards(cards: List[Dict]) -> str:
    """
    Converts flat card dictionaries into readable prompt bullets.
    """
    lines = []
    for card in cards:
        name = card.get("name") or card.get("card_name") or "Unknown Card"
        orientation = card.get("orientation", "upright")
        meaning = card.get("meaning") or card.get("upright_meaning") or ""
        lines.append(f"- {name} ({orientation}): {meaning}")
    return "\n".join(lines)


BASE_PROMPT = """
You are an intuitive tarot reader with deep symbolic insight and a grounded, compassionate voice.

The querent's intention:
"{intention}"

Spread type:
{spread_type}

Cards drawn:
{card_block}

Provide a structured interpretation with the following sections:

1. Summary
   A short 2-3 sentence overview of the reading's emotional and energetic tone.

2. Analysis
   A deeper 3-5 sentence exploration of the symbolism, archetypes, and card relationships.

3. Guidance
   Actionable advice the querent can apply in real life.

4. Affirmation
   A single-sentence affirmation inspired by the reading.

Write in a warm, mystical, and supportive tone. Return plain text.
""".strip()


SPREAD_TEMPLATES = {
    "single": "This is a single-card reading. Focus on the core message and how it directly relates to the querent's intention.",
    "three": (
        "This is a three-card spread. Interpret the cards as past influence, "
        "present situation, and future direction. Explain how the cards interact."
    ),
}


def build_prompt(intention: str, spread_type: str, cards: List[Dict]) -> str:
    card_block = format_cards(cards)
    prompt = BASE_PROMPT.format(
        intention=intention,
        spread_type=spread_type,
        card_block=card_block,
    )

    spread_info = SPREAD_TEMPLATES.get(spread_type.lower(), "")
    if spread_info:
        prompt += "\n\n" + spread_info

    return prompt.strip()
