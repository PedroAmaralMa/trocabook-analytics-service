from typing import Any
from pydantic import BaseModel

class PrevisaoTemporalResponse(BaseModel):
    """
    Representa a estrutura de resposta com as métricas e projeções da previsão temporal.
    """

    avaliacao: dict[str, Any]
    projecoes: list[dict[str, Any]]
    resumoHorizontes: list[dict[str, Any]]
    modelo: dict[str, Any]