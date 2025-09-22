import streamlit as st
from models.item import Item
from db.connection import get_connection
from sqlmodel import Session
from utils.form_generator import render_form


st.title("➕ Ajouter un nouvel item")

# Formulaire dynamique # dépendances pydandic V2 cassée
# item_data = pydantic_form(key="ajout_item_form", model=Item)
item_data = render_form(Item, key_prefix="item_form")

if item_data:
    st.success("✅ Données validées !")

    # Sauvegarde dans la base
    db_conn = get_connection()
    with Session(db_conn.engine, expire_on_commit=False) as session:
        session.add(item_data)
        session.commit()
        st.info(f"Item '{item_data.titre}' ajouté à la bibliothèque.")
