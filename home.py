import streamlit as st
from sqlmodel import SQLModel
from db.connection import get_connection
from models.item import Item  # important pour que le schéma soit connu

st.set_page_config(page_title="Ma biblothèque", page_icon="🧰", layout="wide")


db_conn = get_connection()

df = st.session_state["item_all_df"]

counts = df.group_by("type").count()

cols = st.columns(len(counts))
for col, (cat, nb) in zip(cols, counts.iter_rows()):
    col.metric(label=f"{cat}", value=nb, border=True)
