from sqlmodel import SQLModel, Field
from typing import Optional
from enum import Enum

from sqlalchemy.dialects import sqlite
from sqlalchemy.schema import CreateTable


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


if __name__ == "__main__":
    # Affiche la requête SQL de création de la table Item
    print(Item.__table__)
    sql = str(CreateTable(Item.__table__).compile(dialect=sqlite.dialect()))
    print(sql)
