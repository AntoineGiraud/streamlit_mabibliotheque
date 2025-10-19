import streamlit as st
from models.item import Item
from models.media_type import MediaType


prefix = "item_form"


def init_form_state(item: Item | None = None):
    if not item:
        return None
    print(f"init {item=}")
    for field in Item.__fields__:
        key = f"{prefix}_{field}"
        # Si pas encore initialisé, on met soit la valeur de l'item, soit rien
        if key not in st.session_state:
            val = getattr(item, field) if item else None
            st.session_state[key] = val


def get_form_data() -> dict:
    data = {}
    for field in Item.__fields__:
        key = f"{prefix}_{field}"
        if key in st.session_state:
            data[field] = st.session_state[key]
    return data


def render_fields():
    # Titre sur toute la largeur
    titre = st.text_input("📚 Titre *", key=f"{prefix}_titre", max_chars=200)

    # Ligne 1 : Auteur - Type - Genre
    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        auteur = st.text_input("✍️ Auteur", key=f"{prefix}_auteur")
    with col2:
        type = st.selectbox("🎞 Type *", key=f"{prefix}_type", options=[e.value for e in MediaType])
    with col3:
        genre = st.text_input("🏷 Genre", key=f"{prefix}_genre")

    # Ligne 2 : Année - Note - Langue
    col4, col5, col6 = st.columns([1, 1, 1])
    with col4:
        annee = st.number_input("📅 Année", key=f"{prefix}_annee", min_value=1900, max_value=2030, step=1, format="%d", value=2020)
    with col5:
        note = st.slider("⭐ Note", key=f"{prefix}_note", min_value=0, max_value=5, step=1)
    with col6:
        langue = st.text_input("🌍 Langue", key=f"{prefix}_langue")

    # Ligne 3 : Longueur - Éditeur - Code-barres
    col7, col8, col9 = st.columns([1, 1, 1])
    with col7:
        longueur = st.number_input("📏 Longueur", key=f"{prefix}_longueur", min_value=0, max_value=5000, step=1)
    with col8:
        editeur = st.text_input("🏢 Éditeur", key=f"{prefix}_editeur")
    with col9:
        code = st.text_input("📦 Code-barres", key=f"{prefix}_code")

    # Description pleine largeur
    description = st.text_area("📝 Description", key=f"{prefix}_description", height=100)

    # Couverture sur toute la ligne
    couverture = st.text_input("🖼 URL de la couverture", key=f"{prefix}_couverture")


def render_item_form(item: Item | None = None) -> Item | None:
    init_form_state(item)

    with st.form("item_form", clear_on_submit=False):
        render_fields()

        # Soumission
        submitted = st.form_submit_button("✅ Enregistrer")

        if submitted:
            return submit()

    return None


def submit() -> Item | None:
    try:
        data = get_form_data()

        if not data.get("titre") or not data.get("type"):
            st.warning("Merci de remplir les champs obligatoires : **Titre** et **Type**.")
            return None

        if isinstance(data.get("type"), str):
            data["type"] = MediaType(data["type"])

        item = Item(**data)
        st.success(f"Article '{item.titre}' prêt à être sauvegardé !")
        return item
    except Exception as e:
        st.error(f"Erreur dans la validation des données : {e}")
        return None
