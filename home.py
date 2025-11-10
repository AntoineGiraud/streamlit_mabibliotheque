import streamlit as st

from models.item import Item  # important pour que le schéma soit connu
import db.crud as crud

st.set_page_config(page_title="Ma biblothèque", page_icon="🧰", layout="wide")

# Création des pages pour la navigation
pages = [
    st.Page("pages/0_📚_inventaire.py", title="Inventaire", icon="📚"),
    st.Page("pages/1_🔍_scan_code_barre.py", title="Scan code barre", icon="✍"),
    st.Page("pages/2_📝_ajout_item.py", title="Ajout item", icon="📝"),
]

# Navigation active en position TOP (moderne !)
pg = st.navigation(pages, position="sidebar")
pg.run()

# On fait un peu de cache
if "item_all" not in st.session_state:
    crud.fetch_model_into_streamlitsessionstate(st.session_state, Item)
