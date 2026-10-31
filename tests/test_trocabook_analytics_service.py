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


def test_gerar_relatorio_consolidado_estrutura_completa(
    service,
    mock_anuncio_analytics,
    mock_negociacao_analytics,
    mock_previsao_analytics,
    usuarios_mock
):
    resultado = service.gerar_relatorio_consolidado(
        anuncios=[],
        negociacoes=[],
        usuarios=usuarios_mock,
        horizonte_previsao=12,
        quantidade_teste=4
    )

    assert set(resultado) == {"anuncios", "negociacoes", "previsoes", "insights"}
    assert set(resultado["previsoes"]) == {"anuncios", "usuarios"}

    mock_anuncio_analytics.analisar.assert_called_once_with([])
    mock_negociacao_analytics.analisar.assert_called_once_with([])
    assert mock_previsao_analytics.prever.call_count == 2


def test_consolidacao_de_insights_formatacao_e_origem(service):
    anuncios_insights = ["Insight anúncio 1", "Insight anúncio 2"]
    negociacoes_insights = [{"tipo": "TESTE", "mensagem": "Insight negociação 1"}]

    resultado = service._consolidar_insights(anuncios_insights, negociacoes_insights)

    assert len(resultado) == 3
    assert resultado[0] == {"origem": "ANUNCIOS", "conteudo": "Insight anúncio 1"}
    assert resultado[1] == {"origem": "ANUNCIOS", "conteudo": "Insight anúncio 2"}
    assert resultado[2] == {"origem": "NEGOCIACOES", "conteudo": negociacoes_insights[0]}


def test_prever_anuncios_com_serie_vazia(service, mock_anuncio_analytics, mock_previsao_analytics):
    mock_anuncio_analytics.analisar.return_value = {
        "temporal": {"anunciosPorMes": pd.DataFrame()}
    }

    resultado = service._prever_anuncios(
        analise_anuncios=mock_anuncio_analytics.analisar.return_value,
        horizonte=12,
        quantidade_teste=6
    )

    assert resultado is None
    mock_previsao_analytics.prever.assert_not_called()


def test_prever_anuncios_com_chave_temporal_ausente(service):
    resultado = service._prever_anuncios(
        analise_anuncios={},
        horizonte=12,
        quantidade_teste=6
    )
    assert resultado is None


def test_prever_usuarios_com_lista_vazia(service, mock_previsao_analytics):
    resultado = service._prever_usuarios(
        usuarios=[],
        horizonte=12,
        quantidade_teste=6
    )
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

    resultado = service._prever_usuarios(
        usuarios=usuarios_insuficientes,
        horizonte=12,
        quantidade_teste=6
    )

    assert resultado is None
    mock_previsao_analytics.prever.assert_not_called()


def test_gerar_relatorio_consolidado_sem_usuarios(service):
    resultado = service.gerar_relatorio_consolidado(
        anuncios=[],
        negociacoes=[],
        usuarios=None
    )

    assert resultado["previsoes"]["usuarios"] is None
    assert resultado["previsoes"]["anuncios"] is not None