import streamlit as st
import requests

import db.crud as crud
from db.connection import get_connection

from sqlmodel import Session
from models.item import Item, MediaType

# ------------------------
# CONFIG
# ------------------------

st.set_page_config(page_title="Recherche par code-barres", page_icon="📚")
st.title("Recherche par code-barre 📹📚")


# ------------------------
# FONCTIONS D'APPEL API
# ------------------------
def get_product_metadata(code: int) -> dict:
    """
    Interroge l'API UPCitemdb pour récupérer les infos d'un produit via son code-barres.\n
    doc: https://www.upcitemdb.com/api/explorer#!/lookup/get_trial_lookup
    """
    url = f"https://api.upcitemdb.com/prod/trial/lookup?upc={code}"
    response = requests.get(url)
    response.raise_for_status()

    data = response.json()
    if data.get("code") == "OK" and data.get("total", 0) > 0:
        item = data["items"][0]
        return dict(
            {
                "Titre": item.get("title"),
                "Marque": item.get("brand"),
                "Catégorie": item.get("category"),
                "Couverture": (item.get("images") or [None])[0],
                "Type": "Film" if "dvd" in item.get("category").lower() else item.get("category"),
            },
            **item,
        )
    return None


def fetch_barcode_data(code: int) -> dict:
    """Récupérer les métadonnées de produits (livre, bd, dvd, cd ...) avec l'api la plus adaptée"""
    if not code.is_integer():
        raise "Le code doit être un entier"
    elif str(code).startswith(("978", "979", "977")):
        return Item.get_book_from_isbn(code)
    else:
        return get_product_metadata(code)


# ------------------------
# UI
# ------------------------
code_input = st.number_input(
    "Le code-barres du film ou du livre",
    step=1,
    value=None,
    placeholder="Type a number...",
    key="scanned_item_isbn",
)

if st.button("Rechercher") and code_input:
    with st.spinner("🔍 Recherche en cours..."):
        item = st.session_state["scanned_item"] = fetch_barcode_data(code_input)
    if not item:
        st.info(f"Aucune donnée trouvée pour `{code_input}`")

if st.session_state.get("scanned_item") and st.session_state["scanned_item_isbn"]:
    item = st.session_state["scanned_item"]

    type_detecte = item.type
    type_detecte_emoji = "📚" if type_detecte == "Livre" else "📹"
    st.subheader(f"{type_detecte_emoji} {type_detecte} `{item.titre}`")

    if st.button("Ajouter à ma bibliothèque", type="primary", icon="💾") and code_input:
        db_conn = get_connection()
        with Session(db_conn.engine, expire_on_commit=False) as session:
            session.add(item.copy())
            session.commit()  # On envoie à la base de données

            crud.fetch_model_into_streamlitsessionstate(st.session_state, Item, session)
        st.success(f"{item.titre} ajouté")

    # affichage du résultat en cours
    col_json, col_couverture = st.columns((3, 1))
    col_json.json(item)
    if item.couverture:
        col_couverture.image(item.couverture, caption=item.titre)
