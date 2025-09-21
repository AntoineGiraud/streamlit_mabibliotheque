import streamlit as st
from sqlmodel import create_engine, SQLModel


@st.cache_resource
def get_engine():
    secrets = st.secrets.get("database", {})
    db_type = secrets.get("db_type", "sqlite")
    db_name = secrets.get("db_name", "ma_biblio")

    if db_type == "sqlite":
        db_url = f"sqlite:///{db_name}.db"
    elif db_type == "postgresql":
        db_url = f"postgresql://{secrets['db_user']}:{secrets['db_password']}@{secrets['db_host']}:{secrets['db_port']}/{db_name}"
    elif db_type == "duckdb":
        db_url = f"duckdb:///{db_name}.duckdb"
    else:
        st.error(f"Type de base non supporté : {db_type}")
        return None

    engine = create_engine(db_url, echo=True)

    SQLModel.metadata.create_all(engine, checkfirst=True)

    return engine
