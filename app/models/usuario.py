from datetime import datetime

from pydantic import BaseModel


class Usuario(BaseModel):
    dataCriacao: datetime