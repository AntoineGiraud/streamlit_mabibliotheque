import streamlit as st

from sqlmodel import Session, select
from models.item import Item, MediaType

import db.crud as crud
from db.connection import get_connection
import polars as pl


st.title("📋 Liste interactive des items")


db_conn = get_connection()

# On fait un peu de cache
if "item_all" not in st.session_state:
    crud.fetch_model_into_streamlitsessionstate(st.session_state, Item)

# Édition en place
edited_df = st.data_editor(
    st.session_state["item_all_df"],
    num_rows="dynamic",
    width="content",
    column_config=Item.get_streamlit_column_config(),
    column_order=("titre", "auteur", "annee", "type", "genre", "note", "id", "code"),
    hide_index=True,
)

# Détection des modifications
if st.button("💾 Sauvegarder les modifications"):
    with Session(db_conn.engine) as session:
        print("💾 On sauvegarde")
        recap = crud.sync_dataframe_to_db(session, Item, edited_df, current_items=st.session_state["item_all"])

        if sum(recap.values()) > 0:
            crud.fetch_model_into_streamlitsessionstate(st.session_state, Item, session)

            st.info(f"Modifications enregistrées. {recap=}")

    print(f"    ✅ {recap=}")
