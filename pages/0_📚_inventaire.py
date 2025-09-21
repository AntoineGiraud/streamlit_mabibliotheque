import streamlit as st
import duckdb
import polars as pl
from sqlmodel import Session, select
from db.engine import get_engine
from models.item import Item, MediaType

st.title("📋 Liste interactive des items")

engine = get_engine()
with Session(engine) as session:
    items = session.exec(select(Item)).all()
    items_by_id = {item.id: item for item in items}

# Transformer en DataFrame
df = pl.DataFrame([item.model_dump() for item in items])

column_config = {
    "id": st.column_config.Column("ID", disabled=True, width="small"),
    "titre": st.column_config.TextColumn("Titre", required=True),
    "auteur": st.column_config.TextColumn("Auteur"),
    "annee": st.column_config.NumberColumn("Année", min_value=1900, max_value=2030, step=1, format="%d"),
    "type": st.column_config.SelectboxColumn("Type", options=[e.value for e in MediaType], required=True),
    "genre": st.column_config.TextColumn("Genre"),
    "note": st.column_config.NumberColumn("Note", min_value=0, max_value=5, step=1, format="%d"),
}

# Édition en place
edited_df = st.data_editor(
    df,
    num_rows="dynamic",
    width="stretch",
    column_config=column_config,
    column_order=("titre", "auteur", "annee", "type", "genre", "note", "id"),
)

# Détection des modifications
if st.button("💾 Sauvegarder les modifications"):
    with Session(engine) as session:
        id_restant = []
        for i, row in edited_df.iterrows():
            item = items_by_id.get(row["id"])
            id_restant.append(row["id"])
            print(f"{row=}")
            print(f"{item=}")
            if item and item.model_dump() != row.to_dict():
                item = Item(**row)
                session.add(item)
            elif not item:  # new row ??
                row.pop("id")
                item = Item(**row)
                session.add(item)
        session.commit()

    with Session(engine) as session:
        print("Deletion ??")
        print(f"{id_restant=}")
        # Suppression directe
        for item in items:
            print(f"{item=}")
            if item.id not in id_restant:
                session.delete(item)
        session.commit()

    st.toast("Modifications enregistrées.")
    st.rerun()
