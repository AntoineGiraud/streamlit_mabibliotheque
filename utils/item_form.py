import streamlit as st
from models.item import Item
from models.media_type import MediaType


class ItemForm:
    def __init__(self, item: Item | None = None, prefix="item_form"):
        self.prefix = prefix
        self.item = item
        self.fields = Item.__fields__.keys()
        if self.item:
            self.init_session_state()
            st.info(f"{self.item=}")

    def init_session_state(self):
        for field in self.fields:
            key = f"{self.prefix}_{field}"
            field_value = getattr(self.item, field) if self.item else None
            if key not in st.session_state or st.session_state[key] != field_value:
                if field == "type":
                    st.session_state[key] = field_value.value
                else:
                    st.session_state[key] = field_value

    def render_fields(self):
        # Titre sur toute la largeur
        st.text_input("📚 Titre", key=f"{self.prefix}_titre", max_chars=200)

        # Ligne 1 : Auteur - Type - Genre
        col1, col2, col3 = st.columns([1, 1, 1])
        with col1:
            st.selectbox("🎞 Type", key=f"{self.prefix}_type", options=[e.value for e in MediaType])
        with col2:
            st.text_input("✍️ Auteur", key=f"{self.prefix}_auteur")
        with col3:
            st.text_input("🏷 Genre", key=f"{self.prefix}_genre")

        # Ligne 2 : Année - Note - Langue
        col4, col5, col6 = st.columns([1, 1, 1])
        with col4:
            st.number_input("📅 Année", key=f"{self.prefix}_annee", min_value=1900, max_value=2030, step=1, format="%d")
        with col5:
            st.number_input("⭐ Note", key=f"{self.prefix}_note", min_value=0, max_value=5, step=1)
        with col6:
            st.text_input("🌍 Langue", key=f"{self.prefix}_langue")

        # Ligne 3 : Longueur - Éditeur - Code-barres
        col7, col8, col9 = st.columns([1, 1, 1])
        with col7:
            st.number_input("📏 Longueur", key=f"{self.prefix}_longueur", min_value=0, max_value=5000, step=1)
        with col8:
            st.text_input("🏢 Éditeur", key=f"{self.prefix}_editeur")
        with col9:
            st.number_input("📦 Code-barres", key=f"{self.prefix}_code", step=1)

        # Description pleine largeur
        st.text_area("📝 Description", key=f"{self.prefix}_description", height=100)

        # Couverture sur toute la ligne
        st.text_input("🖼 URL de la couverture", key=f"{self.prefix}_couverture")

    def get_data(self) -> dict:
        data = {}
        for field in self.fields:
            key = f"{self.prefix}_{field}"
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
        with st.form(self.prefix):
            self.render_fields()
            submitted = st.form_submit_button("💾 Enregistrer")
            if submitted:
                return self.submit()
        return None
