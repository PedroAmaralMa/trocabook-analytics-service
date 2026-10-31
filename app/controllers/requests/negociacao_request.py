"""
Módulo do modelo de requisição para análise de negociações.
"""

from pydantic import BaseModel, Field

from app.models.negociacao import Negociacao


class NegociacaoRequest(BaseModel):
    """
    Estrutura de dados recebida na requisição com o contexto necessário para análise das negociações.
    """

    negociacoes: list[Negociacao] = Field(
        default_factory=list,
        description="Lista de negociações registradas.",
    )