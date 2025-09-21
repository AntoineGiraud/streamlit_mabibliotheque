import streamlit as st
import duckdb
import polars as pl
from sqlmodel import Session, select
from db.engine import get_engine
from models.item import Item, MediaType

st.title("📋 Liste interactive des items")

engine = get_engine()
with Session(engine) as session:
    current_items = session.exec(select(Item)).all()
    current_items_by_id = {item.id: item for item in current_items}

# Transformer en DataFrame
df = pl.DataFrame([item.model_dump() for item in current_items])

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
    width="content",
    column_config=column_config,
    column_order=("titre", "auteur", "annee", "type", "genre", "note", "id"),
    hide_index=True,
)

# Détection des modifications
if st.button("💾 Sauvegarder les modifications"):
    with Session(engine) as session:
        items_to_update = []
        items_to_create = []
        existing_ids = set()

        # on repère les insert & update
        for row in edited_df.iter_rows(named=True):
            print(f"  {row=}")
            item_id = row.get("id")

            item = current_items_by_id.get(item_id)
            print(f"  {item=}")
            if item_id and item_id in current_items_by_id:
                existing_ids.add(item_id)
                if item and item.model_dump() != row:
                    item = Item(**row)
                    items_to_update.append(item)
                    session.merge(item)
            elif not item_id:  # new row ??
                row.pop("id")
                item = Item(**row)
                items_to_create.append(item)
                session.add(item)

        # Identifier les items à supprimer
        items_to_delete = [item for item in current_items if item.id not in existing_ids]

        # Suppression directe
        for item in items_to_delete:
            session.delete(item)

        print("Bilan des courses")
        print(f"{items_to_update=}")
        print(f"{items_to_create=}")
        print(f"{items_to_delete=}")

        # allez go on pousse à la db
        session.commit()
        recap = {
            "insert": len(items_to_create),
            "update": len(items_to_update),
            "delete": len(items_to_delete),
        }
    if sum(recap.values()) > 0:
        st.info(f"Modifications enregistrées. {recap=}")
