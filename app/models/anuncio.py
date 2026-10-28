"""
Módulo de definição do modelo de dados de anúncio utilizado pelo serviço de Analytics.
"""

from datetime import datetime

from pydantic import BaseModel

from app.enums.tipo_negociacao import TipoNegociacao


class Anuncio(BaseModel):
    """
    Representa os dados de um anúncio necessários para as análises e previsões do serviço.
    """

    id: str
    uidUsuario: str
    uidLivro: str
    titulo: str
    autores: list[str]
    categorias: list[str]
    tipoNegociacao: TipoNegociacao
    dataCriacao: datetime