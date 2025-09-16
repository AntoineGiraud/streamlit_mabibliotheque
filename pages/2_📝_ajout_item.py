import streamlit as st
from models.item import Item
from db.engine import get_engine
from sqlmodel import Session
from utils.form_generator import render_form
from models.item import Item


st.title("➕ Ajouter un nouvel item")

# Formulaire dynamique # dépendances pydandic V2 cassée
# item_data = pydantic_form(key="ajout_item_form", model=Item)
item_data = render_form(Item, key_prefix="item_form")

if item_data:
    st.success("✅ Données validées !")

    # Sauvegarde dans la base
    engine = get_engine()
    with Session(engine) as session:
        session.add(item_data)
        session.commit()
        st.info(f"Item '{item_data.titre}' ajouté à la bibliothèque.")

if st.button("🔄 Réinitialiser le formulaire"):
    st.experimental_rerun()
