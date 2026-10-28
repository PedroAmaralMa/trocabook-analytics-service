from datetime import datetime

from pydantic import BaseModel

from app.enums.status_negociacao import StatusNegociacao
from app.enums.tipo_negociacao import TipoNegociacao


class Negociacao(BaseModel):
    id: str

    anuncioId: str
    anuncioOferecidoId: str | None = None

    categoriasAnuncio: list[str]
    categoriasAnuncioOferecido: list[str] | None = None

    dataNegociacao: datetime
    dataFinalizacao: datetime | None = None

    tipoNegociacao: TipoNegociacao
    status: StatusNegociacao