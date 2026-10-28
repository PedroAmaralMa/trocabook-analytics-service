"""
Módulo de definição dos possíveis status de uma negociação.
"""

from enum import Enum


class StatusNegociacao(str, Enum):
    """
    Representa os possíveis estados de uma negociação no Trocabook.
    """

    PENDENTE = "PENDENTE"
    EM_ANDAMENTO = "EM_ANDAMENTO"
    RECUSADA = "RECUSADA"
    CANCELADA = "CANCELADA"
    FINALIZADA = "FINALIZADA"