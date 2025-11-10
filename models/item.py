from sqlmodel import SQLModel, Field
from typing import Optional, Dict

from sqlalchemy.dialects import sqlite
from sqlalchemy.schema import CreateTable
from sqlalchemy import JSON
from sqlalchemy import Enum as SAEnum


import streamlit as st

from models.media_type import MediaType


class Item(SQLModel, table=True):
    __table_args__ = {"extend_existing": True}

    id: Optional[int] = Field(default=None, primary_key=True)
    # attributs principaux
    titre: str
    auteur: Optional[str]
    type: MediaType = Field(sa_type=SAEnum(MediaType))
    genre: Optional[str]
    annee: Optional[int] = Field(default=None, ge=1900, le=2030)
    note: Optional[int] = Field(default=None, ge=0, le=5)
    language: Optional[str]
    description: Optional[str]
    longueur: Optional[int] = Field(default=None, ge=0, le=5000)
    # autres champs
    editeur: Optional[str]
    couverture: Optional[str]
    code: Optional[int] = Field(default=None, ge=1e10, le=1e14, index=True)
    other: Optional[dict] = Field(default=None, sa_type=JSON)

    @property
    def label_with_emoji(self) -> str:
        return f"{self.type.emoji} {self.type.value} `{self.titre}`"

    @staticmethod
    def get_streamlit_column_config() -> Dict:
        """Retourne la configuration des colonnes pour st.data_editor."""

        return {
            "id": st.column_config.Column("ID", disabled=True, width="small"),
            "code": st.column_config.Column("Code", disabled=True),
            "titre": st.column_config.TextColumn("Titre", required=True),
            "auteur": st.column_config.TextColumn("Auteur"),
            "annee": st.column_config.NumberColumn("Année", min_value=1900, max_value=2030, step=1, format="%d"),
            "type": st.column_config.SelectboxColumn("Type", options=[e.value for e in MediaType], required=True),
            "genre": st.column_config.TextColumn("Genre"),
            "longueur": st.column_config.NumberColumn("Longueur", min_value=0, max_value=5000, step=1, format="%d"),
            "note": st.column_config.NumberColumn("Note", min_value=0, max_value=5, step=1, format="%d"),
        }


if __name__ == "__main__":
    # Affiche la requête SQL de création de la table Item
    print(Item.__table__)
    sql = str(CreateTable(Item.__table__).compile(dialect=sqlite.dialect()))
    print(sql)
