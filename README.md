# Ma bibliothèque Streamlit 📚

Voici une [app Streamlit](https://bibliotheque.streamlit.app/) pour inventorier le contenu de votre bibliothèque (Livres, BD, DVD, jeux de société ...)

## Fonctionnalités

### 📚 Pages inventaire & éditions

- **📚 Inventaire** : exploration, édition, suppression via un tableau éditable (`st.data_editor`)
- **📝 Ajout / édition manuelle** : Via formulaire "à l'ancienne"

### 🔍 Scan / ajout via le code barre

A partir du code barre, récupération des métadonnées liées & ajoute à l'inventaire

Sources:
- [**google** books api](https://developers.google.com/books/docs/v1/using?hl=fr) pour les livres & BD (1000 appels par jour)\
  *code débutant par 978/979/977*
- [**open4goods**](https://www.data.gouv.fr/datasets/base-de-codes-barres-noms-et-categories-produits/) pour les BD & jeux de société
- [**upc item db**](https://www.upcitemdb.com/api/explorer#!/lookup/get_trial_lookup) en solution de repli (50 appels par jour)

**Note :** étaient pressenties pour rapprocher un code-bare à son film les [datasets IMDb](https://developer.imdb.com/non-commercial-datasets/) ou l'api [omdbapi.com](https://www.omdbapi.com). Malheureusement, ceux-ci ne comportent pas les codes EAN-13 empêchant tout rapprochement.

![demo_recherche_codebarre](./demo_recherche_codebarre.png)


## Installation & commandes

1. Installer uv 👉 cf. [doc astral/uv](https://docs.astral.sh/uv/getting-started/installation/)
2. Lancer l'app streamlit : `uv run streamlit run home.py`

### Astuces développement

- charger le .venv dans le terminal (pour utiliser `streamlit` sans `uv run` avant)
  - `source .venv/bin/activate` (linux) ou `.venv/Scripts/activate.ps1` (windows)
- s'assurer que `pre-commit` est installé
  - `uv run pre-commit install` : initialiser le hook git
    - juste avec ça, sur les prochains fichiers édités, ruff sera lancé automatiquement
  - `uv run pre-commit run --all-files` : pour traiter TOUS les fichiers

## Inspirations & ressources

- by [Gaël Penessot](https://github.com/gpenessot)
  - [Streamlit App Template](https://github.com/gpenessot/streamlit-app-template)
- by Snowflake
  - [Streamlit Getting Started demo](https://docs.snowflake.com/en/developer-guide/streamlit/getting-started#build-your-first-sis-app)
- by Streamlit
  - [Create a multi-app page](https://docs.streamlit.io/get-started/tutorials/create-a-multipage-app)
  - [Snowflake connexion](https://docs.streamlit.io/develop/tutorials/databases/snowflake#write-your-streamlit-app)
- from the Streamlit Community (inventory apps)
  - [Inventory Management System](https://sumaiyaansarihere-inventory-management-system-app-ovsbbn.streamlit.app) by [github/sumaiyaansarihere](https://github.com/sumaiyaansarihere/Inventory-Management-System)
  - [Fresh Grocery Inventory](https://your-repository-name-5p5a7eh584xfpqjrqizvvh.streamlit.app/) by [github/Abdul84-stack](https://github.com/Abdul84-stack/grocery-inventory-app)