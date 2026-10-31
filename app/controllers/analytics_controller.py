"""
Módulo do controller de analytics da API.
"""

from fastapi import APIRouter

from app.adapters.anuncio_adapter import AnuncioAdapter
from app.adapters.negociacao_adapter import NegociacaoAdapter
from app.adapters.previsao_temporal_adapter import PrevisaoTemporalAdapter
from app.controllers.requests.anuncio_request import AnuncioRequest
from app.controllers.requests.negociacao_request import NegociacaoRequest
from app.controllers.requests.previsao_usuarios_request import PrevisaoUsuariosRequest
from app.controllers.responses.anuncio_response import AnuncioResponse
from app.controllers.responses.negociacao_response import NegociacaoResponse
from app.controllers.responses.previsao_temporal_response import (
    PrevisaoTemporalResponse,
)
from app.services.trocabook_analytics_service import TrocabookAnalyticsService

router = APIRouter(prefix="/analytics", tags=["Analytics"])

analytics_service = TrocabookAnalyticsService()


@router.post("/anuncios", response_model=AnuncioResponse)
def analisar_anuncios(request: AnuncioRequest) -> AnuncioResponse:
    """
    Recebe a lista de anúncios e parâmetros para retornar os indicadores e a previsão temporal de anúncios.

    Args:
        request: Objeto de requisição contendo a lista de anúncios, horizonte de previsão e quantidade de teste.

    Returns:
        Objeto AnuncioResponse contendo a análise descritiva e a previsão temporal de anúncios.
    """
    resultado = analytics_service.analisar_anuncios(
        anuncios=request.anuncios,
        horizonte_previsao=request.horizontePrevisao,
        quantidade_teste=request.quantidadeTeste,
    )

    return AnuncioAdapter.para_response(resultado)


@router.post("/negociacoes", response_model=NegociacaoResponse)
def analisar_negociacoes(request: NegociacaoRequest) -> NegociacaoResponse:
    """
    Recebe a lista de negociações para retornar os indicadores descritivos e diagnósticos.

    Args:
        request: Objeto de requisição contendo a lista de negociações.

    Returns:
        Objeto NegociacaoResponse contendo os indicadores gerais, distribuições, afinidades e insights.
    """
    resultado = analytics_service.analisar_negociacoes(negociacoes=request.negociacoes)

    return NegociacaoAdapter.para_response(resultado)


@router.post("/previsao-temporal", response_model=PrevisaoTemporalResponse | None)
def gerar_previsoes_temporais(
    request: PrevisaoUsuariosRequest,
) -> PrevisaoTemporalResponse | None:
    """
    Recebe a lista de usuários para retornar a previsão temporal de novos cadastros.

    Args:
        request: Objeto de requisição contendo a lista de usuários, horizonte de previsão e quantidade de teste.

    Returns:
        Objeto PrevisaoTemporalResponse contendo as projeções e métricas de avaliação, ou None se houver dados insuficientes.
    """
    resultado = analytics_service.gerar_previsoes_temporais(
        usuarios=request.usuarios,
        horizonte_previsao=request.horizontePrevisao,
        quantidade_teste=request.quantidadeTeste,
    )

    return PrevisaoTemporalAdapter.para_response(resultado)