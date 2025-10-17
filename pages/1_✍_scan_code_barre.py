import streamlit as st
import requests

import db.crud as crud
from db.connection import get_connection

from sqlmodel import Session
from models.item import Item
from services.item_service import ItemService


# ------------------------
# CONFIG
# ------------------------

st.set_page_config(page_title="Recherche par code-barres", page_icon="📚")
st.title("Recherche par code-barre 📹📚")


# ------------------------
# UI
# ------------------------

with st.form("scan_form", clear_on_submit=True):
    code_input = st.number_input(
        "Le code-barres du film ou du livre",
        step=1,
        value=None,
        placeholder="Type a number...",
        key="scanned_item_code",
    )
    submitted = st.form_submit_button("Rechercher", type="primary", width="content")
    st.caption("📌 Les éléments sont ajoutés automatiquement")


if submitted and code_input:
    with st.spinner("🔍 Recherche en cours..."):
        db_conn = get_connection()
        with Session(db_conn.engine, expire_on_commit=False) as session:
            item, is_new = ItemService.get_or_create(code_input, session)
            print(f"{item=}, nouveau={is_new}")
            if item and is_new:
                crud.fetch_model_into_streamlitsessionstate(st.session_state, Item, session)
    if item:
        st.subheader(item.label_with_emoji)

        # affichage du résultat en cours
        col_json, col_couverture = st.columns((3, 1))
        col_json.json(item.model_dump())
        if item.couverture:
            col_couverture.image(item.couverture, caption=item.titre)
