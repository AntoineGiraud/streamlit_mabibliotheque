import streamlit as st
from sqlmodel import SQLModel

from models.item import Item  # important pour que le schéma soit connu
import db.crud as crud

st.set_page_config(page_title="Ma biblothèque", page_icon="🧰", layout="wide")


# On fait un peu de cache
if "item_all" not in st.session_state:
    crud.fetch_model_into_streamlitsessionstate(st.session_state, Item)


# --------------------------------
# afficher les stats
# --------------------------------
df = st.session_state["item_all_df"]
counts = df.group_by("type").len()
counts = {cat: nb for cat, nb in counts.iter_rows()}

cols = st.columns(4)
for i, key in enumerate(["Livre", "BD", "DVD", "CD"]):
    cols[i].metric(label=key, value=counts.get(key), border=True)
