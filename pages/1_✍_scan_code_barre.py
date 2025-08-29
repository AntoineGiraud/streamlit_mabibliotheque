import streamlit as st
import requests
import re

# ------------------------
# CONFIG
# ------------------------
OMDB_API_KEY = st.secrets["omdb"]["api_key"]

st.set_page_config(page_title="Recherche par code-barres", page_icon="📚")
st.title("Recherche auto films 📹 / livres 📚 par code-barres")


# ------------------------
# FONCTIONS D'APPEL API
# ------------------------
def get_movie_metadata(query):
    url = f"http://www.omdbapi.com/?apikey={OMDB_API_KEY}&t={query}"
    resp = requests.get(url)
    if resp.status_code == 200:
        data = resp.json()
        print(f"{data=}")
        if data.get("Response") == "True":
            return dict(
                data,
                **{
                    "Titre": data.get("Title"),
                    "Année": data.get("Year"),
                    "Réalisateur": data.get("Director"),
                    "Couverture": data.get("Poster"),
                },
            )
    return None


def get_book_metadata(isbn):
    url = f"https://www.googleapis.com/books/v1/volumes?q=isbn:{isbn}"
    resp = requests.get(url)
    if resp.status_code == 200:
        items = resp.json().get("items")
        if items:
            data = items[0]["volumeInfo"]
            image = data.get("imageLinks", {}).get("thumbnail")
            # return data
            return dict(
                data,
                **{
                    "Titre": data.get("title"),
                    "Auteur": ", ".join(data.get("authors", [])),
                    "Année": data.get("publishedDate"),
                    "Couverture": image,
                },
            )
    return None


def guess_type(code):
    """Devine si c'est un livre ou un film à partir du code."""
    if re.fullmatch(r"\d{10}|\d{13}", code):
        return "Livre/BD"
    else:
        return "Film"


# ------------------------
# UI
# ------------------------
code_input = st.text_input("Le code-barres")

if st.button("Rechercher"):
    if not code_input.strip():
        st.warning("Veuillez entrer un code-barres ou un titre.")
    else:
        with st.spinner("🔍 Recherche en cours..."):
            type_detecte = guess_type(code_input)
            if type_detecte == "Film":
                result = get_movie_metadata(code_input)
            else:
                result = get_book_metadata(code_input)

        if result:
            st.subheader(f"Résultats ({type_detecte})")

            cols = st.columns((3, 1))
            cols[0].json(result)
            img_url = result.get("Couverture")
            if img_url:
                cols[1].image(img_url, caption=result.get("Titre", ""))

        else:
            st.error(f"Aucune donnée trouvée pour ce {type_detecte.lower()}.")
