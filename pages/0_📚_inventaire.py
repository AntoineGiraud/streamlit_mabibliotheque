import streamlit as st

from sqlmodel import Session, select
from models.item import Item, MediaType

import db.crud as crud
import db.engine as engine
import polars as pl


st.title("📋 Liste interactive des items")


engine = engine.get_engine()

# On fait un peu de cache
if "item_all" not in st.session_state:
    with Session(engine) as session:
        items = st.session_state["item_all"] = session.exec(select(Item)).all()
        st.session_state["item_all_df"] = pl.DataFrame([item.model_dump() for item in items])

# Édition en place
edited_df = st.data_editor(
    st.session_state["item_all_df"],
    num_rows="dynamic",
    width="content",
    column_config=Item.get_streamlit_column_config(),
    column_order=("titre", "auteur", "annee", "type", "genre", "note", "id"),
    hide_index=True,
)

# Détection des modifications
if st.button("💾 Sauvegarder les modifications"):
    with Session(engine) as session:
        print("💾 On sauvegarde")

        recap = crud.sync_dataframe_to_db(session, Item, edited_df, current_items=st.session_state["item_all"])
        print(f"💾 Modifications enregistrées. {recap=}")

        if sum(recap.values()) > 0:
            # on actualise le cache
            items = st.session_state["item_all"] = session.exec(select(Item)).all()
            st.session_state["item_all_df"] = pl.DataFrame([item.model_dump() for item in items])

            st.info(f"Modifications enregistrées. {recap=}")
