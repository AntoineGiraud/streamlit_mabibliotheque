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


def fetch_barcode_data(code: int) -> dict:
    """Récupérer les métadonnées de produits (livre, bd, dvd, cd ...) avec l'api la plus adaptée"""
    if not code.is_integer():
        raise "Le code doit être un entier"
    item = None
    if str(code).startswith(("978", "979", "977")):
        item = Item.from_googleapi_books(code)
    if not item:
        item = Item.from_upcitemdb(code)
    return item


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
