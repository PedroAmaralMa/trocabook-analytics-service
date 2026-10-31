"""
Módulo do modelo de requisição para previsão temporal de novos usuários.
"""

from pydantic import BaseModel, Field

from app.models.usuario import Usuario


class PrevisaoUsuariosRequest(BaseModel):
    """
    Estrutura de dados recebida na requisição com o contexto necessário para previsão temporal de usuários.
    """

    usuarios: list[Usuario] = Field(
        default_factory=list,
        description="Lista de usuários registrados.",
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