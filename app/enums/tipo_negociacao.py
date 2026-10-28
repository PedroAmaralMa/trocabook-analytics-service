from enum import Enum


class TipoNegociacao(str, Enum):
    TROCA = "TROCA"
    VENDA = "VENDA"
    AMBOS = "AMBOS"