"""Innovationsfelder: ordnet Veranstaltungen per Stichwort-Abgleich Feldern zu.

Die Klassifizierung passiert beim Build (Titel + Beschreibung + Art). Die Felder
und ihre Stichwörter sind hier zentral definiert und können leicht angepasst werden.
"""
from __future__ import annotations

INNOVATION_FIELDS = [
    {"key": "kreislauf", "label": "Kreislaufwirtschaft",
     "keywords": ["recycling", "kreislauf", "rezyklat", "rezykl", "sekundärrohstoff",
                  "wiederverwert", "circular", "mehrweg", "abfall"]},
    {"key": "nachhaltigkeit", "label": "Nachhaltigkeit & Ressourceneffizienz",
     "keywords": ["nachhalti", "ressourcen", "ökobilanz", "oekobilanz", "co2", "co₂",
                  "klima", "energieeffiz", "sustainab", "umwelt", "biologisch abbaubar"]},
    {"key": "technische", "label": "Technische Textilien",
     "keywords": ["technische textil", "verbund", "composite", "geotextil", "leichtbau",
                  "industrietextil", "faserverbund", "funktionstextil"]},
    {"key": "smart", "label": "Smart Textiles & Digitalisierung",
     "keywords": ["smart textile", "smart-textile", "smarte textil", "sensor", "digital",
                  "künstliche intelligenz", "e-textile", "wearable", "vernetz",
                  "industrie 4.0", "datenökonomie"]},
    {"key": "faser", "label": "Faser- & Materialentwicklung",
     "keywords": ["faser", "biopolymer", "garn", "vliesstoff", "spinn", "polymer",
                  "naturfaser", "materialentwicklung"]},
    {"key": "medizin", "label": "Medizin- & Hygienetextilien",
     "keywords": ["medizin", "hygiene", "antimikrobiell", "wundauflage", "klinik",
                  "gesundheit", "aseptik"]},
    {"key": "bekleidung", "label": "Bekleidung & Komfort",
     "keywords": ["bekleidung", "konfektion", "passform", "komfort", "fashion", "apparel",
                  "körpermaße", "koerpermasse", "konfektionsgröße", "tragekomfort"]},
]


def classify(text: str) -> list[str]:
    """Gibt die Feld-Keys zurück, deren Stichwörter im Text vorkommen (case-insensitive)."""
    t = (text or "").lower()
    keys: list[str] = []
    for field in INNOVATION_FIELDS:
        if any(kw in t for kw in field["keywords"]):
            keys.append(field["key"])
    return keys


def field_defs() -> list[dict]:
    """Feld-Definitionen (key + label) für das Frontend."""
    return [{"key": f["key"], "label": f["label"]} for f in INNOVATION_FIELDS]
