import requests
from typing import Optional
from sqlmodel import Session, select
import streamlit as st

from models.item import Item
from models.media_type import MediaType


class ItemService:
    @staticmethod
    def get_or_create(code: int, session: Session) -> tuple[Optional["Item"], bool]:
        if not isinstance(code, int):
            raise ValueError("Le code doit être un entier")

        item = session.exec(select(Item).where(Item.code == code)).first()
        if item:
            st.info(f"{item.type.title} déjà présent dans la biblithèque")
            return item, False  # ← EXISTANT

        item = ItemService.from_barcode(code, session)
        if item:
            session.add(item)
            st.success(f"{item.type.title} ajouté à la bibliothèque")
            session.commit()
            return item, True  # ← NOUVEAU

        st.warning(f"Aucune donnée trouvée pour `{code}`")
        return None, False

    @staticmethod
    def from_barcode(code: int, session: Session) -> Optional["Item"]:
        """Essaie de récupérer un item (livre, bd, dvd, cd ...)  via ISBN ou UPC"""
        if not isinstance(code, int):
            raise ValueError("Le code doit être un entier")

        item = None
        if str(code).startswith(("978", "979", "977")):
            item = ItemService.from_googleapi_books(code)
        if not item:  # allez on essaie avec upc, google n'a rien trouvé
            item = ItemService.from_upcitemdb(code)

        return item

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
