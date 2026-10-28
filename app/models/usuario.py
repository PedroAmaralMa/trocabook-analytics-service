"""
Módulo de definição do modelo de dados de usuário utilizado pelo serviço de Analytics.
"""

from datetime import datetime

from pydantic import BaseModel


class Usuario(BaseModel):
    """
    Representa os dados de um usuário necessários para a previsão de novos usuários.
    """

    dataCriacao: datetime