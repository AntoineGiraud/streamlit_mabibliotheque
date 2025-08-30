import streamlit as st
import requests

# ------------------------
# CONFIG
# ------------------------
OMDB_API_KEY = st.secrets["omdb"]["api_key"]

st.set_page_config(page_title="Recherche par code-barres", page_icon="📚")
st.title("Recherche par code-barre 📹📚")


# ------------------------
# FONCTIONS D'APPEL API
# ------------------------
def get_product_metadata(code: int) -> dict:
    """
    Interroge l'API UPCitemdb pour récupérer les infos d'un produit via son code-barres.\n
    doc: https://www.upcitemdb.com/api/explorer#!/lookup/get_trial_lookup
    """
    url = f"https://api.upcitemdb.com/prod/trial/lookup?upc={code}"
    response = requests.get(url)
    response.raise_for_status()

    data = response.json()
    if data.get("code") == "OK" and data.get("total", 0) > 0:
        item = data["items"][0]
        return dict(
            {
                "Titre": item.get("title"),
                "Marque": item.get("brand"),
                "Catégorie": item.get("category"),
                "Couverture": (item.get("images") or [None])[0],
                "Type": "Film" if "dvd" in item.get("category").lower() else item.get("category"),
            },
            **item,
        )
    return None


def get_movie_metadata(title: str) -> dict:
    """
    Récupérer des données imdb d'un film ...\n
    mais imposible depuis un code barre EAN-13... donc on écarte\n
    i pour un code imdb, t pour un titre\n
    doc: https://www.omdbapi.com/
    """
    url = f"http://www.omdbapi.com/?apikey={OMDB_API_KEY}&t={title}"
    response = requests.get(url)
    response.raise_for_status()

    item = response.json()
    print(f"{item=}")
    if item.get("Response") == "True":
        return dict(
            {
                "Titre": item.get("Title"),
                "Année": item.get("Year"),
                "Réalisateur": item.get("Director"),
                "Couverture": item.get("Poster"),
                "Type": "Film",
            },
            **item,
        )
    return None


def get_book_metadata(isbn: int) -> dict:
    url = f"https://www.googleapis.com/books/v1/volumes?q=isbn:{isbn}"
    response = requests.get(url)
    response.raise_for_status()

    items = response.json().get("items")
    if items:
        item = items[0]["volumeInfo"]
        image = item.get("imageLinks", {}).get("thumbnail")
        # return item
        return dict(
            {
                "Titre": item.get("title"),
                "Auteur": ", ".join(item.get("authors", [])),
                "Année": item.get("publishedDate"),
                "Couverture": image,
                "Type": "Livre",
            },
            **item,
        )
    return None


def fetch_barcode_data(code: int) -> dict:
    """Récupérer les métadonnées de produits (livre, bd, dvd, cd ...) avec l'api la plus adaptée"""
    if not code.is_integer():
        raise "Le code doit être un entier"
    elif str(code).startswith(("978", "979", "977")):
        return get_book_metadata(code)
    else:
        return get_product_metadata(code)


# ------------------------
# UI
# ------------------------
code_input = st.number_input(
    "Le code-barres du film ou du livre",
    step=1,
    value=None,
    placeholder="Type a number...",
)

if st.button("Rechercher") and code_input:
    with st.spinner("🔍 Recherche en cours..."):
        result = fetch_barcode_data(code_input)
        type_detecte = result.get("Type")
        type_detecte_emoji = "📚" if type_detecte == "Livre" else "📹"

    if result:
        st.subheader(f"{type_detecte_emoji} {type_detecte} `{result.get('Titre', '')}`")

        if st.button("Ajouter à ma bibliothèque", type="primary", icon="💾") and code_input:
            pass

        cols = st.columns((3, 1))
        cols[0].json(result)
        img_url = result.get("Couverture")
        if img_url:
            cols[1].image(img_url, caption=result.get("Titre", ""))

    else:
        st.info(f"Aucune donnée trouvée pour `{type_detecte.lower()}`")
