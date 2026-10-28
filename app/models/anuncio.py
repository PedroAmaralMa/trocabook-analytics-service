from datetime import datetime

from pydantic import BaseModel

from app.enums.tipo_negociacao import TipoNegociacao


class Anuncio(BaseModel):
    id: str
    uidUsuario: str
    uidLivro: str

    titulo: str
    autores: list[str]
    categorias: list[str]

    tipoNegociacao: TipoNegociacao
    dataCriacao: datetime