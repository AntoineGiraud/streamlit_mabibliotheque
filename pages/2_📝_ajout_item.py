import streamlit as st

from models import Item, MediaType
from db.connection import get_connection
from sqlmodel import Session
from utils.form_generator import render_form
from utils.render_item_form import render_item_form

from db import crud

st.title("📝 Ajouter un nouvel item")

# Formulaire dynamique # dépendances pydandic V2 cassée
# item_data = pydantic_form(key="ajout_item_form", model=Item)
# item_data = render_form(Item, key_prefix="item_form")

item_to_edit = None  # charger un Item si besoin

item = render_item_form(item_to_edit)

if item:
    st.success(f"✅ Données validées ! {item.label_with_emoji}")

    # Sauvegarde dans la base
    db_conn = get_connection()
    with Session(db_conn.engine, expire_on_commit=False) as session:
        session.add(item)
        session.commit()
        st.info(f"Item '{item.titre}' ajouté à la bibliothèque.")

        crud.fetch_model_into_streamlitsessionstate(st.session_state, Item, session)
