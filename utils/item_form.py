import streamlit as st
from models.item import Item
from models.media_type import MediaType


class ItemForm:
    PREFIX = "item_form"
    ITEM_FIELDS = Item.__fields__.keys()

    def __init__(self):
        pass

    @staticmethod
    def init_session_state(item: Item | None):
        for field in ItemForm.ITEM_FIELDS:
            key = f"{ItemForm.PREFIX}_{field}"
            field_value = getattr(item, field) if item else None
            if field == "type" and item:
                st.session_state[key] = field_value.value
            else:
                st.session_state[key] = field_value

    @staticmethod
    def render_fields():
        # Titre sur toute la largeur
        st.text_input("📚 Titre", key=f"{ItemForm.PREFIX}_titre", max_chars=200)

        # Ligne 1 : Auteur - Type - Genre
        col1, col2, col3 = st.columns([1, 1, 1])
        col1.selectbox("🎞 Type", key=f"{ItemForm.PREFIX}_type", options=[e.value for e in MediaType])
        col2.text_input("✍️ Auteur", key=f"{ItemForm.PREFIX}_auteur")
        col3.text_input("🏷 Genre", key=f"{ItemForm.PREFIX}_genre")

        # Ligne 2 : Année - Note - Langue
        col4, col5, col6 = st.columns([1, 1, 1])
        col4.number_input("📅 Année", key=f"{ItemForm.PREFIX}_annee", min_value=1900, max_value=2030, step=1, format="%d")
        col5.number_input("⭐ Note", key=f"{ItemForm.PREFIX}_note", min_value=0, max_value=5, step=1)
        col6.text_input("🌍 Langue", key=f"{ItemForm.PREFIX}_langue")

        # Ligne 3 : Longueur - Éditeur - Code-barres
        col7, col8, col9 = st.columns([1, 1, 1])
        col7.number_input("📏 Longueur", key=f"{ItemForm.PREFIX}_longueur", min_value=0, max_value=5000, step=1)
        col8.text_input("🏢 Éditeur", key=f"{ItemForm.PREFIX}_editeur")
        col9.number_input("📦 Code-barres", key=f"{ItemForm.PREFIX}_code", step=1)

        # Description pleine largeur
        st.text_area("📝 Description", key=f"{ItemForm.PREFIX}_description", height=100)

        # Couverture sur toute la ligne
        st.text_input("🖼 URL de la couverture", key=f"{ItemForm.PREFIX}_couverture")

    @staticmethod
    def get_data() -> dict:
        data = {}
        for field in ItemForm.ITEM_FIELDS:
            key = f"{ItemForm.PREFIX}_{field}"
            if key in st.session_state:
                data[field] = st.session_state[key]

        # Conversion explicite pour enums
        if isinstance(data.get("type"), str):
            data["type"] = MediaType(data["type"])

        return data

    def submit(self) -> Item | None:
        try:
            data = self.get_data()

            if not data.get("titre") or not data.get("type"):
                st.warning("Merci de remplir les champs obligatoires : **Titre** et **Type**.")
                return None

            item = Item(**data)
            st.success(f"Article '{item.titre}' prêt à être sauvegardé !")
            return item
        except Exception as e:
            st.error(f"Erreur dans la validation des données : {e}")
            return None

    def render(self) -> Item | None:
        with st.form(ItemForm.PREFIX):
            self.render_fields()
            submitted = st.form_submit_button("💾 Enregistrer")
            if submitted:
                return self.submit()
        return None
