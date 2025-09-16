import streamlit as st
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
edited_df = st.data_editor(df, num_rows="dynamic", use_container_width=True)

# Détection des modifications
if st.button("💾 Sauvegarder les modifications"):
    with Session(engine) as session:
        for i, row in edited_df.iterrows():
            item = session.get(Item, row["id"])
            if item:
                for field in row.index:
                    setattr(item, field, row[field])
                session.add(item)
        session.commit()
        st.success("Modifications enregistrées.")

# Suppression directe
for i, row in df.iterrows():
    if st.button(f"🗑️ Supprimer {row['titre']}", key=f"delete_{row['id']}"):
        with Session(engine) as session:
            item = session.get(Item, row["id"])
            if item:
                session.delete(item)
                session.commit()
                st.rerun()
