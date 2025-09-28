from sqlmodel import SQLModel, Field
from typing import Optional, Dict
import requests

from sqlalchemy.dialects import sqlite
from sqlalchemy.schema import CreateTable
from sqlalchemy import JSON

import streamlit as st

from models.media_type import MediaType


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
    longueur: Optional[int] = Field(default=None, ge=0, le=5000)
    # autres champs
    editeur: Optional[str]
    couverture: Optional[str]
    code: Optional[int] = Field(default=None, ge=1e10, le=1e14)
    other: Optional[dict] = Field(default=None, sa_type=JSON)

    @property
    def label_with_emoji(self) -> str:
        return f"{self.type.emoji} {self.type.value} `{self.titre}`"

    @staticmethod
    def get_streamlit_column_config() -> Dict:
        """Retourne la configuration des colonnes pour st.data_editor."""

        return {
            "id": st.column_config.Column("ID", disabled=True, width="small"),
            "code": st.column_config.Column("Code", disabled=True),
            "titre": st.column_config.TextColumn("Titre", required=True),
            "auteur": st.column_config.TextColumn("Auteur"),
            "annee": st.column_config.NumberColumn("Année", min_value=1900, max_value=2030, step=1, format="%d"),
            "type": st.column_config.SelectboxColumn("Type", options=[e.value for e in MediaType], required=True),
            "genre": st.column_config.TextColumn("Genre"),
            "longueur": st.column_config.NumberColumn("Longueur", min_value=0, max_value=5000, step=1, format="%d"),
            "note": st.column_config.NumberColumn("Note", min_value=0, max_value=5, step=1, format="%d"),
        }

    @staticmethod
    @st.cache_data
    def from_googleapi_books(code: int) -> SQLModel:
        """Fetch book from googleapis.com by it's isbn code"""
        url = f"https://www.googleapis.com/books/v1/volumes?q=isbn:{code}"
        response = requests.get(url)
        response.raise_for_status()

        items = response.json().get("items")
        if items:
            item = items[0]["volumeInfo"]
            # print(f"{item=}")
            final = {
                "type": "Livre",
                "genre": item.get("categories", [None])[0],
                "code": code,
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

    @staticmethod
    @st.cache_data
    def from_upcitemdb(code: int) -> SQLModel:
        """
        Fetch book from UPCitemdb.com by it's code\n
        doc: https://www.upcitemdb.com/api/explorer#!/lookup/get_trial_lookup
        """

        url = f"https://api.upcitemdb.com/prod/trial/lookup?upc={code}"
        response = requests.get(url)
        response.raise_for_status()

        data = response.json()
        if data.get("code") == "OK" and data.get("total", 0) > 0:
            item = data["items"][0]
            fianl = dict(
                {
                    "Titre": item.get("title"),
                    "Marque": item.get("brand"),
                    "Catégorie": item.get("category"),
                    "Couverture": (item.get("images") or [None])[0],
                    "Type": "Film" if "dvd" in item.get("category").lower() else item.get("category"),
                },
                **item,
            )
            final = {
                "type": "Livre",
                "genre": item.get("categories", [None])[0],
                "code": code,
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
