from sqlmodel import SQLModel, Field, select, Session
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
    code: Optional[int] = Field(default=None, ge=1e10, le=1e14, index=True)
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

    @classmethod
    def get_or_create(cls, code: int, session: Session) -> Optional["Item"]:
        if not isinstance(code, int):
            raise ValueError("Le code doit être un entier")

        item = session.exec(select(cls).where(cls.code == code)).first()
        if item:
            st.info(f"{item.type.title} déjà présent dans la biblithèque")
            return item

        item = cls.from_barcode(code, session)
        if item:
            session.add(item)
            st.success(f"{item.type.title} ajouté à la bibliothèque")
            session.commit()
            return item

        st.warning(f"Aucune donnée trouvée pour `{code}`")
        return None

    @classmethod
    def from_barcode(cls, code: int, session: Session) -> Optional["Item"]:
        """Récupérer les métadonnées de produits (livre, bd, dvd, cd ...) avec l'API la plus adaptée"""
        if not isinstance(code, int):
            raise ValueError("Le code doit être un entier")

        item = None
        if str(code).startswith(("978", "979", "977")):
            item = cls.from_googleapi_books(code)
        if not item:  # allez on essaie avec upc, google n'a rien trouvé
            item = cls.from_upcitemdb(code)
        return item

    @classmethod
    @st.cache_data
    def from_googleapi_books(cls, code: int) -> Optional["Item"]:
        """Fetch book from googleapis.com by its ISBN code and return an Item instance"""
        url = f"https://www.googleapis.com/books/v1/volumes?q=isbn:{code}"
        response = requests.get(url)
        if not response.ok:
            return None

        items = response.json().get("items")
        if items:
            item: dict = items[0]["volumeInfo"]
            final = {
                "type": "Livre",
                "genre": item.get("categories", [None])[0],
                "code": code,
                "titre": item.get("title"),
                "auteur": ", ".join(item.get("authors", [])),
                "annee": int(item.get("publishedDate", "0000")[:4]) or None,
                "language": item.get("language"),
                "longueur": item.get("pageCount"),
                "editeur": item.get("publisher"),
                "couverture": item.get("imageLinks", {}).get("thumbnail"),
            }

            # retirer les champs principaux déjà extraits
            for key in ["categories", "title", "authors", "publishedDate", "language", "pageCount", "publisher", "imageLinks", "industryIdentifiers", "readingModes", "panelizationSummary"]:
                item.pop(key, None)

            # faire le ménage & retirer les valeurs vides
            for k, v in item.copy().items():
                if not v:
                    item.pop(k, None)

            final["other"] = item
            return cls(**final)
        return None

    @classmethod
    @st.cache_data
    def from_upcitemdb(cls, code: int) -> Optional["Item"]:
        """
        Fetch book from UPCitemdb.com by it's code\n
        doc: https://www.upcitemdb.com/api/explorer#!/lookup/get_trial_lookup
        """

        url = f"https://api.upcitemdb.com/prod/trial/lookup?upc={code}"
        response = requests.get(url)
        if not response.ok:
            return None

        data = response.json()
        if data.get("code") == "OK" and data.get("total", 0) > 0:
            item: dict = data["items"][0]
            final = {
                "type": MediaType.from_upc_category(item.get("category")),
                "code": code,
                "titre": item.get("title").strip("."),
                "annee": int(item.get("publishedDate", "0000")[:4]) or None,
                "editeur": item.get("publisher") or item.get("brand"),
                "couverture": (item.get("images") or [None])[0],
            }
            if final.get("couverture") and "no_image" in final.get("couverture").lower():
                final.pop("couverture", None)

            # retirer les champs principaux déjà extraits
            for key in ["title", "authors", "publishedDate", "language", "pageCount", "images", "offers", "publisher", "brand"]:
                item.pop(key, None)

            # faire le ménage & retirer les valeurs vides
            for k, v in item.copy().items():
                if not v:
                    item.pop(k, None)

            final["other"] = item
            return cls(**final)
        return None


if __name__ == "__main__":
    # Affiche la requête SQL de création de la table Item
    print(Item.__table__)
    sql = str(CreateTable(Item.__table__).compile(dialect=sqlite.dialect()))
    print(sql)
