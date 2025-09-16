from sqlmodel import SQLModel, Field
from typing import Optional
from enum import Enum


class MediaType(str, Enum):
    CD = "CD"
    LIVRE = "Livre"
    BD = "BD"
    DVD = "DVD"


class Item(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    # Pour DuckDB, pas besoin de SERIAL, juste INTEGER avec default=None
    titre: str
    auteur: Optional[str]
    annee: Optional[int] = Field(default=None, ge=1900, le=2030)
    type: MediaType
    genre: Optional[str]
    note: Optional[int] = Field(default=None, ge=0, le=5)
