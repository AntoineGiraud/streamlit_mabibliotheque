import streamlit as st
import duckdb
import pandas as pd
from sqlmodel import Session, select
from db.engine import get_engine
from models.item import Item

st.title("📋 Liste interactive des items")

engine = get_engine()
with Session(engine) as session:
    items = session.exec(select(Item)).all()

# Transformer en DataFrame
df = pd.DataFrame([item.model_dump() for item in items])

# Édition en place
edited_df = st.data_editor(df, num_rows="dynamic", width="stretch")

# Détection des modifications
if st.button("💾 Sauvegarder les modifications"):
    with Session(engine) as session:
        for i, row in edited_df.iterrows():
            item = session.get(Item, row["id"])
            if item:
                for field in row.index:
                    setattr(item, field, row[field])
                session.add(item)
            else:  # new row ??
                item = Item(**row)
                session.add(item)
        session.commit()
        st.success("Modifications enregistrées.")

    with Session(engine) as session:
        # Suppression directe
        for i, row in df.iterrows():
            item = session.get(Item, row["id"])
            if item:
                session.delete(item)
                session.commit()
                st.rerun()
