"""
Module CRUD générique pour les opérations de base de données.
Fournit des fonctions réutilisables pour synchroniser des DataFrames avec la DB.
"""

import polars as pl

from typing import List, Dict, Any, TypeVar, Type, Tuple, Optional
from sqlmodel import SQLModel, Session, select
from models.item import Item, MediaType

from db.connection import get_connection

T = TypeVar("T", bound=SQLModel)


def fetch_model_into_streamlitsessionstate(
    session_state,
    model_class: Type[T] = Item,
    session: Session = None,
):
    if not session:
        db_conn = get_connection()
        with Session(db_conn.engine) as s:
            session = s

    class_name = model_class.__name__.lower()
    # on actualise le cache
    items = session_state[f"{class_name}_all"] = session.exec(select(model_class)).all()
    session_state[f"{class_name}_all_df"] = pl.DataFrame([item.model_dump(exclude=["other"]) for item in items])


def sync_dataframe_to_db(
    session: Session,
    model_class: Type[T],
    edited_df: pl.DataFrame,
    current_items: Optional[Dict] = {},
    id_column: str = "id",
) -> Dict[str, int]:
    """
    Synchronise un DataFrame Polars avec la base de données.

    Args:
        session: Session SQLModel active
        model_class: Classe du modèle SQLModel (ex: Item)
        edited_df: DataFrame avec les données éditées
        id_column: Nom de la colonne ID (défaut: "id")

    Returns:
        Dict avec le nombre d'opérations: {"insert": int, "update": int, "delete": int}
    """

    # Récupérer les items actuels de la DB
    if not current_items:
        current_items = session.exec(select(model_class)).all()

    current_items_by_id = {getattr(item, id_column): item for item in current_items}

    # Listes pour tracker les opérations
    items_to_update = []
    items_to_create = []
    existing_ids = set()

    # Analyser chaque ligne du DataFrame édité
    for row in edited_df.iter_rows(named=True):
        item_id = row.get(id_column)

        if item_id and item_id in current_items_by_id:
            # Item existant - vérifier s'il y a des changements
            existing_item = current_items_by_id[item_id]
            existing_ids.add(item_id)

            if existing_item.model_dump(exclude=["other"]) != row:
                # Créer un nouvel objet avec les données mises à jour
                updated_item = model_class(**row)
                items_to_update.append(updated_item)
                session.merge(updated_item)

        elif not item_id or item_id == "":
            # Nouvel item à créer
            row_data = row.copy()
            if id_column in row_data:
                row_data.pop(id_column)  # Laisser l'auto-increment

            new_item = model_class(**row_data)
            items_to_create.append(new_item)
            session.add(new_item)

    # Identifier les items à supprimer
    items_to_delete = [item for item in current_items if getattr(item, id_column) not in existing_ids]
    for item in items_to_delete:
        session.delete(item)

    # On envoie à la base de données
    session.commit()

    return {
        "insert": len(items_to_create),
        "update": len(items_to_update),
        "delete": len(items_to_delete),
    }
