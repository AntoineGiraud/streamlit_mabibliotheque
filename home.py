import streamlit as st
from sqlmodel import SQLModel
from db.engine import get_engine
from models.item import Item  # important pour que le schéma soit connu

st.set_page_config(page_title="Ma biblothèque", page_icon="🧰", layout="wide")


engine = get_engine()


with open("README.md", "r", encoding="utf-8") as file:
    readme_contents = file.read()
    st.markdown(readme_contents.replace("# ", "## "), unsafe_allow_html=True)
