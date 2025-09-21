from sqlmodel import SQLModel, Field
from typing import Optional, Dict
from enum import Enum

from sqlalchemy.dialects import sqlite
from sqlalchemy.schema import CreateTable

from streamlit import column_config


class MediaType(str, Enum):
    CD = "CD"
    LIVRE = "Livre"
    BD = "BD"
    DVD = "DVD"


class Item(SQLModel, table=True):
    __table_args__ = {"extend_existing": True}

    id: Optional[int] = Field(default=None, primary_key=True)
    titre: str
    auteur: Optional[str]
    annee: Optional[int] = Field(default=None, ge=1900, le=2030)
    type: MediaType
    genre: Optional[str]
    note: Optional[int] = Field(default=None, ge=0, le=5)
    # other: Optional[dict]

    def get_streamlit_column_config() -> Dict:
        """Retourne la configuration des colonnes pour st.data_editor."""

        return {
            "id": column_config.Column("ID", disabled=True, width="small"),
            "titre": column_config.TextColumn("Titre", required=True),
            "auteur": column_config.TextColumn("Auteur"),
            "annee": column_config.NumberColumn("Année", min_value=1900, max_value=2030, step=1, format="%d"),
            "type": column_config.SelectboxColumn("Type", options=[e.value for e in MediaType], required=True),
            "genre": column_config.TextColumn("Genre"),
            "note": column_config.NumberColumn("Note", min_value=0, max_value=5, step=1, format="%d"),
        }


if __name__ == "__main__":
    # Affiche la requête SQL de création de la table Item
    print(Item.__table__)
    sql = str(CreateTable(Item.__table__).compile(dialect=sqlite.dialect()))
    print(sql)
