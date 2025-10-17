from enum import Enum
from typing import Optional


class MediaType(str, Enum):
    CD = "CD"
    Livre = "Livre"
    BD = "BD"
    DVD = "DVD"
    Jeu = "Jeu"

    @property
    def emoji(self) -> str:
        return {
            MediaType.CD: "💿",
            MediaType.Livre: "📖",
            MediaType.BD: "📚",
            MediaType.DVD: "🎬",
            MediaType.Jeu: "🎲",
        }.get(self, "❓")

    @property
    def title(self) -> str:
        return f"{self.emoji} {self.value}"

    @classmethod
    def from_upc_category(cls, category: str) -> Optional["MediaType"]:
        cat = category.lower()
        if "dvd" in cat:
            return cls("DVD")
        elif "book" in cat:
            return cls("Livre")
        return None
