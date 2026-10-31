"""
Ponto de entrada da aplicação FastAPI do serviço de analytics.
"""

import logging

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.controllers.analytics_controller import router as analytics_router
from app.exceptions.analytics_exception import AnalyticsException

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s | %(levelname)s | %(name)s | %(message)s"
)

app = FastAPI(title="Trocabook - Serviço de Analytics", version="1.0.0")

app.include_router(analytics_router)


@app.exception_handler(AnalyticsException)
async def analytics_exception_handler(request: Request, exc: AnalyticsException):
    """
    Manipula exceções do tipo AnalyticsException retornando resposta HTTP 500 padronizada.

    Args:
        request: Objeto de requisição HTTP do FastAPI.
        exc: Instância da exceção AnalyticsException capturada.

    Returns:
        JSONResponse com status code 500 e mensagem de detalhe do erro.
    """
    return JSONResponse(status_code=500, content={"detail": str(exc)})


@app.get("/")
def root():
    """
    Retorna uma mensagem de status e identificação do serviço.
    """
    return {"message": "Trocabook - Serviço de Analytics"}