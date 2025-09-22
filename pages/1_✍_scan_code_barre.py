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


def save_item(item):
    db_conn = get_connection()
    with Session(db_conn.engine, expire_on_commit=False) as session:
        session.add(item.copy())
        session.commit()
        crud.fetch_model_into_streamlitsessionstate(st.session_state, Item, session)
    st.success(f"{item.titre} ajouté à la bibliothèque")
    st.session_state["scanned_item"] = None


# ------------------------
# UI
# ------------------------

with st.expander("Ajout automatique ?"):
    auto_add_to_db = st.checkbox(
        "Ajouter automatiquement à la bibliothèque après la recherche",
        key="auto_add_to_db",
        value=True,
    )
if auto_add_to_db:
    st.caption("📌 Les éléments seront ajoutés automatiquement après chaque recherche.")


with st.form("scan_form", clear_on_submit=True):
    code_input = st.number_input(
        "Le code-barres du film ou du livre",
        step=1,
        value=None,
        placeholder="Type a number...",
        key="scanned_item_code",
    )
    submitted = st.form_submit_button("Rechercher")


if submitted and code_input:
    with st.spinner("🔍 Recherche en cours..."):
        item = st.session_state["scanned_item"] = fetch_barcode_data(code_input)
    if not item:
        st.info(f"Aucune donnée trouvée pour `{code_input}`")

if st.session_state.get("scanned_item"):
    item = st.session_state["scanned_item"]

    type_detecte = item.type
    type_detecte_emoji = "📚" if type_detecte == "Livre" else "📹"
    st.subheader(f"{type_detecte_emoji} {type_detecte} `{item.titre}`")

    if auto_add_to_db or st.button("Ajouter à ma bibliothèque", type="primary", icon="💾"):
        save_item(item)

    # affichage du résultat en cours
    col_json, col_couverture = st.columns((3, 1))
    col_json.json(item)
    if item.couverture:
        col_couverture.image(item.couverture, caption=item.titre)
