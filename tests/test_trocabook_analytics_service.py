from datetime import datetime
from unittest.mock import MagicMock

import pandas as pd
import pytest

from app.service.trocabook_analytics_service import TrocabookAnalyticsService


@pytest.fixture
def mock_anuncio_analytics():
    analytics = MagicMock()
    analytics.analisar.return_value = {
        "geral": {"totalAnuncios": 10},
        "temporal": {
            "anunciosPorMes": pd.DataFrame({
                "mesCriacao": pd.period_range("2024-01", periods=10, freq="M"),
                "novosAnuncios": [5, 8, 12, 15, 18, 20, 22, 25, 28, 30]
            })
        },
        "insights": ["A categoria mais frequente é Ficção."]
    }
    return analytics


@pytest.fixture
def mock_negociacao_analytics():
    analytics = MagicMock()
    analytics.analisar.return_value = {
        "geral": {"totalNegociacoes": 5},
        "insights": [
            {
                "tipo": "TIPO_NEGOCIACAO",
                "titulo": "Desempenho por tipo",
                "mensagem": "Trocas apresentaram maior taxa de finalização."
            }
        ]
    }
    return analytics


@pytest.fixture
def mock_previsao_analytics():
    analytics = MagicMock()
    analytics.prever.return_value = {
        "avaliacao": {"mae": 1.2, "rmse": 1.5},
        "projecoes": pd.DataFrame({"quantidadeEstimada": [32, 35, 38]}),
        "resumoHorizontes": pd.DataFrame({"horizonteMeses": [1, 3]}),
        "modelo": {"coeficiente": 2.5, "intercepto": 10.0}
    }
    return analytics


@pytest.fixture
def service(mock_anuncio_analytics, mock_negociacao_analytics, mock_previsao_analytics):
    return TrocabookAnalyticsService(
        anuncio_analytics=mock_anuncio_analytics,
        negociacao_analytics=mock_negociacao_analytics,
        previsao_analytics=mock_previsao_analytics
    )


@pytest.fixture
def usuarios_mock():
    class UsuarioMock:
        def __init__(self, data_criacao):
            self.dataCriacao = data_criacao

    datas = pd.date_range("2024-01-01", periods=10, freq="MS")
    return [UsuarioMock(data) for data in datas]


def test_inicializacao_com_dependencias_padrao():
    service_padrao = TrocabookAnalyticsService()
    assert service_padrao.anuncio_analytics is not None
    assert service_padrao.negociacao_analytics is not None
    assert service_padrao.previsao_analytics is not None


def test_analisar_anuncios_sucesso(service, mock_anuncio_analytics, mock_previsao_analytics):
    resultado = service.analisar_anuncios(
        anuncios=[],
        horizonte_previsao=12,
        quantidade_teste=4
    )

    assert set(resultado) == {"analise", "previsao"}
    mock_anuncio_analytics.analisar.assert_called_once_with([])
    mock_previsao_analytics.prever.assert_called_once()


def test_analisar_negociacoes_sucesso(service, mock_negociacao_analytics):
    resultado = service.analisar_negociacoes(negociacoes=[])

    assert resultado == mock_negociacao_analytics.analisar.return_value
    mock_negociacao_analytics.analisar.assert_called_once_with([])


def test_gerar_previsoes_temporais_sucesso(service, mock_previsao_analytics, usuarios_mock):
    resultado = service.gerar_previsoes_temporais(
        usuarios=usuarios_mock,
        horizonte_previsao=12,
        quantidade_teste=4
    )

    assert resultado == mock_previsao_analytics.prever.return_value
    mock_previsao_analytics.prever.assert_called_once()


def test_prever_anuncios_com_serie_vazia(service, mock_anuncio_analytics, mock_previsao_analytics):
    mock_anuncio_analytics.analisar.return_value = {
        "temporal": {"anunciosPorMes": pd.DataFrame()}
    }

    resultado = service.analisar_anuncios(anuncios=[])

    assert resultado["analise"] is not None
    assert resultado["previsao"] is None
    mock_previsao_analytics.prever.assert_not_called()


def test_prever_anuncios_com_chave_temporal_ausente(service):
    resultado = service._prever_anuncios(
        analise_anuncios={},
        horizonte=12,
        quantidade_teste=6
    )
    assert resultado is None


def test_prever_usuarios_com_lista_vazia(service, mock_previsao_analytics):
    resultado = service.gerar_previsoes_temporais(usuarios=[])
    assert resultado is None
    mock_previsao_analytics.prever.assert_not_called()


def test_prever_usuarios_com_historico_insuficiente(service, mock_previsao_analytics):
    class UsuarioMock:
        def __init__(self, data):
            self.dataCriacao = data

    usuarios_insuficientes = [
        UsuarioMock(datetime(2024, 1, 1)),
        UsuarioMock(datetime(2024, 2, 1)),
        UsuarioMock(datetime(2024, 3, 1))
    ]

    resultado = service.gerar_previsoes_temporais(
        usuarios=usuarios_insuficientes,
        horizonte_previsao=12,
        quantidade_teste=6
    )

    assert resultado is None
    mock_previsao_analytics.prever.assert_not_called()


def test_consolidar_insights(service):
    anuncios_insights = ["Insight 1"]
    negociacoes_insights = [{"tipo": "TESTE", "mensagem": "Insight 2"}]

    resultado = service._consolidar_insights(anuncios_insights, negociacoes_insights)

    assert len(resultado) == 2
    assert resultado[0] == {"origem": "ANUNCIOS", "conteudo": "Insight 1"}
    assert resultado[1] == {"origem": "NEGOCIACOES", "conteudo": negociacoes_insights[0]}