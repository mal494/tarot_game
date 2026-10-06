# Divine Insight Core dependency

Arcana Path (a sister brand to Divine Insight) gets all of its card data from
[mal494/divine-insight-core](https://github.com/mal494/divine-insight-core).
No card data is edited by hand in this repo.

## Pinned to Core

```
core.version = v1.6.1
```

| File | What it is |
| --- | --- |
| `core.version` | The pinned Core release |
| `data/core/tarot_data_v1.6.1.json` | Vendored copy of Core's `data/tarot_data_v1.6.1.json` |
| `data/core/art_manifest.json` | Vendored copy of Core's `art/manifest.json` (card slug to artwork file) |
| `tools/generate_cards.py` | Builds `assets/data/tarot_cards.json` from the two files above |
| `assets/data/tarot_cards.json` | Generated. Do not edit. |

## How the game's card file is built

`tools/generate_cards.py` reads the pinned Core dataset and flattens each card into the
shape the game loads:

| Game field | From Core |
| --- | --- |
| `id` | position in Core's card list (0-77), kept so existing journal entries line up |
| `key`, `slug`, `number` | same names |
| `card_name` | `name` |
| `short_description` | same name |
| `arcana_type`, `card_type` | `arcana`, `card_type` |
| `suit` | `suit`, with Core's `"None"` turned into `null` for the Major Arcana |
| `element`, `elemental_weight`, `astrology` | same names |
| `tags`, `life_domains` | same names |
| `upright_meaning`, `reversed_meaning` | `meanings.upright/reversed.description` |
| `keywords`, `reversed_keywords` | `meanings.upright/reversed.keywords` |
| `positional_text`, `positional_weights` | same names |
| `image_path`, `thumbnail_path` | `assets/cards/major|minor/<file>.jpg` and `assets/cards/thumbnails/thumb_<file>.jpg`, where `<file>` comes from the art manifest |

## Upgrading Core

1. Wait for the new Core release to be tagged.
2. Copy its `data/tarot_data_vX.Y.json` into `data/core/` and refresh `data/core/art_manifest.json`.
3. Set `core.version` to the new tag and delete the old vendored dataset.
4. Run `python tools/generate_cards.py`.
5. Run the tests. `tests/test_core_data.py` fails if the card file is out of date with `core.version`.
