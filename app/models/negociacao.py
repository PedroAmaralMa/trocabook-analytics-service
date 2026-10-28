"""
Módulo de definição do modelo de dados de negociação utilizado pelo serviço de Analytics.
"""

from datetime import datetime

from pydantic import BaseModel

from app.enums.status_negociacao import StatusNegociacao
from app.enums.tipo_negociacao import TipoNegociacao


class Negociacao(BaseModel):
    """
    Representa os dados de uma negociação necessários para as análises do serviço.
    """

    id: str

    anuncioId: str
    anuncioOferecidoId: str | None = None

    categoriasAnuncio: list[str]
    categoriasAnuncioOferecido: list[str] | None = None

    dataNegociacao: datetime
    dataFinalizacao: datetime | None = None

    tipoNegociacao: TipoNegociacao
    status: StatusNegociacao