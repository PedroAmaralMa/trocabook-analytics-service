"""
Módulo dos modelos de resposta para análise de anúncios.
"""

from typing import Any
from pydantic import BaseModel
from app.controllers.responses.previsao_temporal_response import PrevisaoTemporalResponse

class AnuncioAnaliseResponse(BaseModel):
    """
    Representa a estrutura de resposta com os indicadores descritivos da análise de anúncios.
    """

    geral: dict[str, Any]
    porTipo: list[dict[str, Any]]
    porAutor: list[dict[str, Any]]
    porCategoria: list[dict[str, Any]]
    categoriaPorTipo: dict[str, Any]
    temporal: dict[str, Any]
    insights: list[str]


class AnuncioResponse(BaseModel):
    """
    Representa o contrato de resposta consolidado retornado pela API para anúncios.
    """

    analise: AnuncioAnaliseResponse
    previsao: PrevisaoTemporalResponse | None = None