import streamlit as st
from sqlmodel import Session

from models import Item
from db.connection import get_connection
from utils.item_form import ItemForm
from db import crud


def update_selected_item_id(selected_item, session_state_key="selected_item_id"):
    prev_id = st.session_state.get(session_state_key, "__unset__")
    new_id = selected_item.id if selected_item else None
    if new_id != prev_id:
        st.session_state[session_state_key] = new_id
        ItemForm.init_session_state(selected_item)
        st.rerun()


# ⬆️ Titre
st.title("📝 Ajouter ou modifier un item")

all_items = st.session_state["item_all"]

# 🧠 Init du state
if "selected_item_id" not in st.session_state:
    st.session_state.selected_item_id = None

# 🧱 Construction des options avec emoji
select_options = [("➕ Ajouter un nouvel item", None)]
for itm in sorted(all_items, key=lambda i: (i.type.value, i.titre.lower())):
    label = f"{itm.type.emoji} {itm.titre}"
    select_options.append((label, itm))

# 🔽 Selectbox pour choisir l’item
selected_label, selected_item = st.selectbox(
    "🔍 Choisissez un item à modifier (ou rien pour en ajouter un nouveau)",
    options=select_options,
    format_func=lambda x: x[0],
    index=0,  # par défaut : "ajouter"
)

# 🔁 Mise à jour du state + forcer reload si changement
update_selected_item_id(selected_item)

# 🔄 Retrouver l’item à partir du state (pour cohérence sur tous les runs)
item_to_edit = next((i for i in all_items if i.id == st.session_state.selected_item_id), None)

# 📝 Afficher le formulaire
item = ItemForm().render()

# 💾 Traitement après validation du formulaire
if item:
    st.success(f"✅ Données validées ! {item.label_with_emoji}")

    # 🆔 Si on modifie un item, il faut lui réinjecter l'id
    if item_to_edit and not item.id:
        item.id = item_to_edit.id

    db_conn = get_connection()
    with Session(db_conn.engine, expire_on_commit=False) as session:
        session.merge(item)
        session.commit()
        st.info(f"Item '{item.titre}' enregistré dans la bibliothèque.")

        # Refresh du cache d'objets
        crud.fetch_model_into_streamlitsessionstate(st.session_state, Item, session)
