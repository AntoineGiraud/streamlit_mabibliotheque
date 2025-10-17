import streamlit as st
from models.item import Item
from models.media_type import MediaType


def render_item_form() -> Item | None:
    with st.form("item_form", clear_on_submit=False):
        # Titre sur toute la largeur
        titre = st.text_input("📚 Titre *", max_chars=200)

        # Ligne 1 : Auteur - Type - Genre
        col1, col2, col3 = st.columns([1, 1, 1])
        with col1:
            auteur = st.text_input("✍️ Auteur")
        with col2:
            type_ = st.selectbox("🎞 Type *", options=[e.value for e in MediaType])
        with col3:
            genre = st.text_input("🏷 Genre")

        # Ligne 2 : Année - Note - Langue
        col4, col5, col6 = st.columns([1, 1, 1])
        with col4:
            annee = st.number_input("📅 Année", min_value=1900, max_value=2030, step=1, format="%d", value=2020)
        with col5:
            note = st.slider("⭐ Note", min_value=0, max_value=5, step=1)
        with col6:
            langue = st.text_input("🌍 Langue")

        # Ligne 3 : Longueur - Éditeur - Code-barres
        col7, col8, col9 = st.columns([1, 1, 1])
        with col7:
            longueur = st.number_input("📏 Longueur", min_value=0, max_value=5000, step=1)
        with col8:
            editeur = st.text_input("🏢 Éditeur")
        with col9:
            code = st.text_input("📦 Code-barres")

        # Description pleine largeur
        description = st.text_area("📝 Description", height=100)

        # Couverture sur toute la ligne
        couverture = st.text_input("🖼 URL de la couverture")

        # Soumission
        submitted = st.form_submit_button("✅ Enregistrer")

        if submitted:
            if not titre or not type_:
                st.warning("Merci de remplir les champs obligatoires : **Titre** et **Type**.")
                return None

            # Nettoyage des données
            return Item(
                titre=titre.strip(),
                auteur=auteur or None,
                type=MediaType(type_),
                genre=genre or None,
                annee=int(annee) if annee else None,
                note=int(note) if note else None,
                language=langue or None,
                description=description or None,
                longueur=int(longueur) if longueur else None,
                editeur=editeur or None,
                couverture=couverture or None,
                code=int(code) if code else None,
            )

    return None
