"""
Módulo do modelo de resposta de negociações da API.
"""

from typing import Any
from pydantic import BaseModel


class NegociacaoResponse(BaseModel):
    """
    Representa os indicadores e diagnósticos das negociações retornados pela API.
    """

    geral: dict[str, Any]
    porTipo: list[dict[str, Any]]
    porCategoria: list[dict[str, Any]]
    afinidadeCategorias: list[dict[str, Any]]
    combinacoesCategorias: list[dict[str, Any]]
    temporal: dict[str, Any]
    insights: list[Any]