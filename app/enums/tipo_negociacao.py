"""
Módulo de definição dos tipos de negociação utilizados pelo Trocabook.
"""

from enum import Enum


class TipoNegociacao(str, Enum):
    """
    Representa os tipos de negociação disponíveis no Trocabook.
    """

    TROCA = "TROCA"
    VENDA = "VENDA"
    AMBOS = "AMBOS"