import streamlit as st

from models import Item, MediaType
from db.connection import get_connection
from sqlmodel import Session, select
from utils.item_form import ItemForm
from db import crud
from collections import defaultdict

st.title("📝 Ajouter ou modifier un item")

# 1. Connexion DB pour charger les articles
db_conn = get_connection()
with Session(db_conn.engine, expire_on_commit=False) as session:
    items = session.exec(select(Item)).all()

# 2. Construire les options avec emoji par type de média
# Option 0 : ajout d'un nouvel item
select_options = [("➕ Ajouter un nouvel item", None)]

# Ajouter tous les items avec emoji devant le titre
for item in sorted(items, key=lambda x: (x.type.value, x.titre.lower())):
    emoji = item.type.emoji
    label = f"{emoji} {item.titre}"
    select_options.append((label, item))

# 3. Afficher la selectbox
selected_label, item_to_edit = st.selectbox(
    "🔍 Choisissez un item à modifier (ou rien pour en ajouter un nouveau)",
    options=select_options,
    format_func=lambda x: x[0],
)

# 4. Formulaire avec ou sans données
item = ItemForm(item_to_edit).render()

# 5. Traitement du formulaire
if item:
    st.success(f"✅ Données validées ! {item.label_with_emoji}")

    # Sauvegarde dans la base
    db_conn = get_connection()
    with Session(db_conn.engine, expire_on_commit=False) as session:
        session.add(item)
        session.commit()
        st.info(f"Item '{item.titre}' enregistré dans la bibliothèque.")

        crud.fetch_model_into_streamlitsessionstate(st.session_state, Item, session)
