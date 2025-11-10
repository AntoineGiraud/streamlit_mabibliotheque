import streamlit as st
from sqlalchemy import func
from sqlmodel import SQLModel, select, Session
from models.item import Item
import db.crud as crud


from streamlit.runtime.secrets import StreamlitSecretNotFoundError


def load_database_secrets():
    try:
        secrets = st.secrets.get("database", {})
    except StreamlitSecretNotFoundError:
        st.warning("⚠️ Fichier `secrets.toml` manquant. Utilisation des valeurs par défaut. `sqlite:///db/ma_biblio.db`")
        secrets = {"db_type": "sqlite", "db_name": "ma_biblio"}
    return secrets


@st.cache_resource
def get_connection():
    secrets = load_database_secrets()
    db_type = secrets.get("db_type", "sqlite")
    db_name = secrets.get("db_name", "ma_biblio")

    if db_type == "sqlite":
        db_url = f"sqlite:///db/{db_name}.db"
    elif db_type == "postgresql":
        db_url = f"postgresql://{secrets['db_user']}:{secrets['db_password']}@{secrets['db_host']}:{secrets['db_port']}/{db_name}"
    elif db_type == "duckdb":
        db_url = f"duckdb:///{db_name}.duckdb"

    else:
        st.error(f"Type de base non supporté : {db_type}")
        return None

    db_conn = st.connection("sql", url=db_url, type="sql")

    # Création des tables si elles n'existent pas
    SQLModel.metadata.create_all(db_conn.engine, checkfirst=True)

    with Session(db_conn.engine) as session:
        nb_items = session.exec(select(func.count()).select_from(Item)).one()

        # Si aucun item, insérer quelques exemples
        if not nb_items:
            exemples = [
                Item(titre="Livre A", type="Livre"),
                Item(titre="Livre B", type="Livre"),
                Item(titre="Livre C", type="Livre"),
                Item(titre="CD A", type="CD"),
                Item(titre="DVD B", type="DVD"),
                Item(titre="BD C", type="BD"),
            ]
            session.add_all(exemples)
            session.commit()

        # Charger dans session_state
        crud.fetch_model_into_streamlitsessionstate(st.session_state, Item, session)

    return db_conn
