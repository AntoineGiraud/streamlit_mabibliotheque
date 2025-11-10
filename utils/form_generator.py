from typing import Optional, get_args, get_origin, Union
from pydantic import BaseModel, ValidationError
import streamlit as st
from enum import Enum


def extract_base_type(field_type):
    """Retourne le type réel si Optional[...] ou Union[..., None]"""
    if get_origin(field_type) in {Union, Optional}:
        args = [arg for arg in get_args(field_type) if arg is not type(None)]
        return args[0] if args else str
    return field_type


def render_form(model_class: type[BaseModel], key_prefix: str = "") -> Optional[BaseModel]:
    st.subheader(f"Formulaire : {model_class.__name__}")
    inputs = {}

    for field_name, field_info in model_class.model_fields.items():
        field_type = extract_base_type(field_info.annotation)
        default = field_info.default
        # required = field_info.is_required()

        widget_key = f"{key_prefix}_{field_name}"

        # Enum
        if isinstance(field_type, type) and issubclass(field_type, Enum):
            options = [e.value for e in field_type]
            index = options.index(default) if default in options else 0
            inputs[field_name] = st.selectbox(field_name, options, key=widget_key, index=index)

        # Int
        elif field_type is int:
            value = default if default is not None else 0
            inputs[field_name] = st.number_input(field_name, value=value, step=1, key=widget_key)

        # Float
        elif field_type is float:
            value = default if default is not None else 0.0
            inputs[field_name] = st.number_input(field_name, value=value, step=0.1, key=widget_key)

        # Str
        elif field_type is str:
            value = default if default is not None else ""
            inputs[field_name] = st.text_input(field_name, value=value, key=widget_key)

        else:
            st.warning(f"Type non géré : {field_info.annotation}")

        # Si le champ est facultatif, permettre de le vider
        # if not required and st.checkbox(f"❌ Supprimer la valeur de '{field_name}'", key=f"{widget_key}_clear"):
        #     inputs[field_name] = None

    if st.button("✅ Valider", key=f"{key_prefix}_submit"):
        try:
            return model_class(**inputs)
        except ValidationError as e:
            st.error(f"Erreur de validation : {e}")
            return None

    return None
