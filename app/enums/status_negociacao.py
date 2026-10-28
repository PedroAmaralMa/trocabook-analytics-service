from enum import Enum


class StatusNegociacao(str, Enum):
    PENDENTE = "PENDENTE"
    EM_ANDAMENTO = "EM_ANDAMENTO"
    RECUSADA = "RECUSADA"
    CANCELADA = "CANCELADA"
    FINALIZADA = "FINALIZADA"