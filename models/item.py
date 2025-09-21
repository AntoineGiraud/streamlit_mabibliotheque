from sqlmodel import SQLModel, Field
from typing import Optional, Dict
from enum import Enum
import requests

from sqlalchemy.dialects import sqlite
from sqlalchemy.schema import CreateTable
from sqlalchemy import JSON

from streamlit import column_config


class MediaType(str, Enum):
    CD = "CD"
    Livre = "Livre"
    BD = "BD"
    DVD = "DVD"


class Item(SQLModel, table=True):
    __table_args__ = {"extend_existing": True}

    id: Optional[int] = Field(default=None, primary_key=True)
    # attributs principaux
    titre: str
    auteur: Optional[str]
    type: MediaType
    genre: Optional[str]
    annee: Optional[int] = Field(default=None, ge=1900, le=2030)
    note: Optional[int] = Field(default=None, ge=0, le=5)
    language: Optional[str]
    description: Optional[str]
    longueur: Optional[int]
    # autres champs
    editeur: Optional[str]
    couverture: Optional[str]
    isbn: Optional[int] = Field(default=None, ge=1e10, le=1e14)
    other: Optional[dict] = Field(default=None, sa_type=JSON)

    @staticmethod
    def get_streamlit_column_config() -> Dict:
        """Retourne la configuration des colonnes pour st.data_editor."""

        return {
            "id": column_config.Column("ID", disabled=True, width="small"),
            "isbn": column_config.Column("Isbn", disabled=True),
            "titre": column_config.TextColumn("Titre", required=True),
            "auteur": column_config.TextColumn("Auteur"),
            "annee": column_config.NumberColumn("Année", min_value=1900, max_value=2030, step=1, format="%d"),
            "type": column_config.SelectboxColumn("Type", options=[e.value for e in MediaType], required=True),
            "genre": column_config.TextColumn("Genre"),
            "longueur": column_config.NumberColumn("Longueur", min_value=0, max_value=5000, step=1, format="%d"),
            "note": column_config.NumberColumn("Note", min_value=0, max_value=5, step=1, format="%d"),
        }

    @staticmethod
    def get_book_from_isbn(isbn: int) -> SQLModel:
        """Fetch book from isbn & init Item"""
        url = f"https://www.googleapis.com/books/v1/volumes?q=isbn:{isbn}"
        response = requests.get(url)
        response.raise_for_status()

        items = response.json().get("items")
        if items:
            item = items[0]["volumeInfo"]
            # print(f"{item=}")
            final = {
                "type": "Livre",
                "genre": item.get("categories", [None])[0],
                "isbn": isbn,
                "titre": item.get("title"),
                "auteur": ", ".join(item.get("authors", [])),
                "annee": int(item.get("publishedDate")[:4]),
                "language": item.get("language"),
                "longueur": item.get("pageCount"),
                "editeur": item.get("publisher"),
                "couverture": item.get("imageLinks", {}).get("thumbnail"),
            }

            # on garde pour l'instant au cas où les autres champs de l'api
            for key in ["categories", "title", "authors", "publishedDate", "language", "pageCount", "publisher", "imageLinks", "industryIdentifiers", "readingModes", "panelizationSummary"]:
                item.pop(key, None)
            final["other"] = item

            return Item(**final)
        return None


if __name__ == "__main__":
    # Affiche la requête SQL de création de la table Item
    print(Item.__table__)
    sql = str(CreateTable(Item.__table__).compile(dialect=sqlite.dialect()))
    print(sql)
