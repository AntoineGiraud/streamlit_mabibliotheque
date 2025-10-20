import requests
from typing import Optional
from sqlmodel import Session, select
import streamlit as st

from models.item import Item
from models.media_type import MediaType

import duckdb
import os


class ItemService:
    @staticmethod
    def get_or_create(code: int, session: Session) -> tuple[Optional["Item"], bool]:
        if not isinstance(code, int):
            raise ValueError("Le code doit être un entier")

        item = session.exec(select(Item).where(Item.code == code)).first()
        if item:
            st.info(f"{item.type.title} déjà présent dans la biblithèque")
            return item, False  # ← EXISTANT

        item = ItemService.from_barcode(code)
        if item:
            session.add(item)
            st.success(f"{item.type.title} ajouté à la bibliothèque")
            session.commit()
            return item, True  # ← NOUVEAU

        st.warning(f"Aucune donnée trouvée pour `{code}`")
        return None, False

    @staticmethod
    def from_barcode(code: int) -> Optional[Item]:
        """Essaie de récupérer un item (livre, bd, dvd, cd, jeu ...) via GTIN"""
        if not isinstance(code, int):
            raise ValueError("Le code doit être un entier")

        # 1. Jeux de société ? (avant tout)
        item = ItemService.from_local_boardgame_dataset(code)
        if item:
            return item

        # 2. ISBN → Google
        if str(code).startswith(("978", "979", "977")):
            item = ItemService.from_googleapi_books(code)
            if item:
                return ItemService.enrich_with_local_bd_data(item, code)

            # 3. Fallback BD locale
            item = ItemService.from_local_bd_dataset(code)
            if item:
                return item

        # 4. Sinon, dernier fallback UPC
        return ItemService.from_upcitemdb(code)

    @staticmethod
    def from_local_boardgame_dataset(code: int) -> Optional[Item]:
        """Essaie de créer un Item depuis le fichier local s'il correspond à un jeu de société"""
        parquet_path = "data/gtin_jeuxDeSociete.parquet"
        if not os.path.exists(parquet_path):
            return None

        try:
            result = duckdb.sql(f"""
                SELECT name, brand
                FROM '{parquet_path}'
                WHERE gtin = {code}
                LIMIT 1
            """).fetchone()
        except Exception as e:
            st.warning(f"Erreur DuckDB (jeu de société) : {e}")
            return None

        if result:
            print(f"🎲 jeu trouvé {result=}")
            name, brand = result
            return Item(
                code=code,
                titre=name or "Jeu sans nom",
                editeur=brand,
                type=MediaType("Jeu"),
                genre="Jeu de société",
            )

        return None

    def fetch_BD_from_parquet(code: int) -> dict | None:
        """Cherche dans le .parquet si l'ISBN correspond à une BD et la retourne"""
        parquet_path = "data/isbn_nudger_BD.parquet"
        if not os.path.exists(parquet_path):
            return None  # Fichier absent → rien à faire

        query = f"""
            SELECT title as titre, editeur, TRY_CAST(nb_page as int) as longueur, classification_decitre_2 as genre
            FROM '{parquet_path}'
            WHERE isbn = {code}
            LIMIT 1
        """

        try:
            result = duckdb.sql(query).fetchone()
            return dict(zip(("titre", "editeur", "longueur", "genre"), result)) if result else None
        except Exception as e:
            st.warning(f"Erreur DuckDB : {e}")
            return None

    @staticmethod
    def enrich_with_local_bd_data(item: Item, code: int) -> Item:
        """Cherche dans le .parquet si l'ISBN correspond à une BD et enrichit l'item"""
        if result := ItemService.fetch_BD_from_parquet(code):
            item.type = MediaType.BD
            for attr, value in result.items():
                if value:
                    setattr(item, attr, value)
        return item

    @staticmethod
    def from_local_bd_dataset(code: int) -> Optional[Item]:
        """Construit un Item à partir des données locales si le code correspond à une BD"""
        if result := ItemService.fetch_BD_from_parquet(code):
            return Item(type=MediaType.BD, **result)

        return None

    @staticmethod
    @st.cache_data
    def from_googleapi_books(code: int) -> Optional["Item"]:
        """Fetch book from googleapis.com by its ISBN code and return an Item instance"""
        url = f"https://www.googleapis.com/books/v1/volumes?q=isbn:{code}"
        response = requests.get(url)
        if not response.ok:
            return None

        items = response.json().get("items")
        if items:
            item: dict = items[0]["volumeInfo"]
            final = {
                "type": MediaType.Livre,
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
            return Item(**final)
        return None

    @staticmethod
    @st.cache_data
    def from_upcitemdb(code: int) -> Optional["Item"]:
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
            return Item(**final)
        return None
