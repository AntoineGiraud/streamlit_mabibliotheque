import streamlit as st
import requests


st.set_page_config(page_title="Lookup Code-Barres", layout="centered")
st.title("Recherche de métadonnées par code-barres")

# 1. Input
barcode = st.text_input("Entrez un code-barres (ISBN / UPC)")

media_type = st.selectbox("Type de média", ("Livre", "Film", "BD"))

# 2. Bouton
if st.button("Récupérer les métadonnées"):
    if not barcode:
        st.warning("Merci de renseigner un code-barres valide.")
    else:
        with st.spinner("Chargement…"):

            def fetch_livre(isbn):
                url = f"https://openlibrary.org/api/books"
                params = {
                    "bibkeys": f"ISBN:{isbn}",
                    "format": "json",
                    "jscmd": "data",
                }
                resp = requests.get(url, params=params)
                data = resp.json()
                return data.get(f"ISBN:{isbn}", {})

            def fetch_film(upc):
                # Exemple avec l'API OMDb (nécessite une clé API à obtenir sur http://www.omdbapi.com/)
                API_KEY = st.secrets["omdb"]["api_key"]
                params = {
                    "apikey": API_KEY,
                    "i": upc,
                }
                resp = requests.get("http://www.omdbapi.com/", params=params)
                return resp.json()

            def fetch_bd(upc):
                # Stub : à remplacer par une vraie API (ex. ComicVine) ou par une base locale
                fake_data = {"titre": "Exemple BD", "auteur": "Jane Doe", "éditeur": "Éditions Fictives", "année": 2020}
                return fake_data

            # Choix de la fonction selon le type
            if media_type == "Livre":
                metadata = fetch_livre(barcode)
            elif media_type == "Film":
                metadata = fetch_film(barcode)
            else:  # BD
                metadata = fetch_bd(barcode)

        # 3. Affichage
        if metadata:
            st.subheader("Métadonnées récupérées")
            st.json(metadata)
        else:
            st.error("Aucune donnée trouvée pour ce code-barres.")
