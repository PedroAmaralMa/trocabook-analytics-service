"""
Módulo do modelo de requisição para análise de anúncios.
"""

from pydantic import BaseModel, Field

from app.models.anuncio import Anuncio


class AnuncioRequest(BaseModel):
    """
    Estrutura de dados recebida na requisição com o contexto necessário para análise dos anúncios.
    """

    anuncios: list[Anuncio] = Field(
        default_factory=list,
        description="Lista de anúncios cadastrados.",
    )
    horizontePrevisao: int = Field(
        default=12,
        ge=1,
        description="Quantidade de meses futuros a serem projetados.",
    )
    quantidadeTeste: int = Field(
        default=6,
        ge=1,
        description="Quantidade de meses reservados para validação do modelo de regressão.",
    )