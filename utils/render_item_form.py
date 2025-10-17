import streamlit as st
from models.item import Item
from models.media_type import MediaType


def render_item_form() -> Item | None:
    with st.form("item_form", clear_on_submit=False):
        # Champs principaux
        titre = st.text_input("Titre", max_chars=200)
        auteur = st.text_input("Auteur")
        type_ = st.selectbox("Type", options=[e.value for e in MediaType])
        genre = st.text_input("Genre")
        annee = st.number_input("Année", min_value=1900, max_value=2030, step=1, format="%d")
        note = st.slider("Note (0 à 5)", min_value=0, max_value=5, step=1)
        langue = st.text_input("Langue")
        description = st.text_area("Description", height=100)
        longueur = st.number_input("Longueur (pages, minutes…)", min_value=0, max_value=5000, step=1)

        # Champs complémentaires
        editeur = st.text_input("Éditeur")
        couverture = st.text_input("URL de la couverture")
        code = st.number_input("Code-barres", min_value=1e10, max_value=1e14, step=1.0, format="%.0f")

        submitted = st.form_submit_button("✅ Enregistrer", type="primary")

        if submitted:
            if not titre or not type_:
                st.warning("Merci de remplir les champs obligatoires : Titre et Type.")
                return None

            return Item(
                titre=titre,
                auteur=auteur or None,
                type=MediaType(type_),
                genre=genre or None,
                annee=int(annee) if annee else None,
                note=note,
                language=langue or None,
                description=description or None,
                longueur=int(longueur) if longueur else None,
                editeur=editeur or None,
                couverture=couverture or None,
                code=int(code) if code else None,
            )

    return None
