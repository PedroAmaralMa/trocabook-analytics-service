"""Testes unitários da classe PrevisaoTemporalAnalytics."""
import numpy as np
import pandas as pd
import pytest

from app.analytics.previsao_temporal_analytics import PrevisaoTemporalAnalytics


@pytest.fixture
def analytics():
    return PrevisaoTemporalAnalytics()


@pytest.fixture
def serie_mensal():
    return pd.DataFrame({
        "mesCriacao": pd.period_range("2023-01", periods=24, freq="M"),
        "novosUsuarios": [
            10, 12, 13, 15, 14, 17, 18, 20, 22, 21, 24, 25,
            27, 29, 28, 31, 32, 35, 34, 37, 39, 40, 42, 44
        ]
    })

def test_prever_retorna_estrutura_esperada(analytics, serie_mensal):
    resultado = analytics.prever(
        serie_mensal,
        coluna_valor="novosUsuarios"
    )

    assert set(resultado) == {
        "avaliacao", "projecoes", "resumoHorizontes", "modelo"
    }
    assert {"mae", "rmse", "previsoesTeste"} <= set(resultado["avaliacao"])
    assert len(resultado["projecoes"]) == 12
    assert resultado["resumoHorizontes"]["horizonteMeses"].tolist() == [1, 3, 6, 12]

def test_prever_aceita_serie_de_anuncios(analytics):
    serie = pd.DataFrame({
        "mesCriacao": pd.date_range("2024-01-01", periods=18, freq="MS"),
        "novosAnuncios": list(range(5, 23))
    })

    resultado = analytics.prever(serie, coluna_valor="novosAnuncios")

    assert len(resultado["projecoes"]) == 12
    assert resultado["projecoes"]["quantidadeEstimada"].dtype.kind in "iu"


def test_preparar_serie_completa_meses_ausentes(analytics):
    serie = pd.DataFrame({
        "mesCriacao": ["2024-01", "2024-03"],
        "quantidade": [4, 7]
    })

    preparada = analytics._preparar_serie_temporal(
        serie, "mesCriacao", "quantidade"
    )

    assert preparada["quantidade"].tolist() == [4.0, 0.0, 7.0]
    assert preparada["indiceTempo"].tolist() == [0, 1, 2]


def test_prever_rejeita_dataframe_vazio(analytics):
    with pytest.raises(ValueError, match="não pode estar vazia"):
        analytics.prever(pd.DataFrame(columns=["mesCriacao", "quantidade"]))


def test_prever_rejeita_coluna_ausente(analytics):
    serie = pd.DataFrame({"mesCriacao": ["2024-01"]})

    with pytest.raises(ValueError, match="Colunas obrigatórias ausentes"):
        analytics.prever(serie)


def test_prever_rejeita_meses_duplicados(analytics):
    serie = pd.DataFrame({
        "mesCriacao": ["2024-01", "2024-01"],
        "quantidade": [2, 3]
    })

    with pytest.raises(ValueError, match="apenas um registro por mês"):
        analytics.prever(serie)


def test_prever_rejeita_valores_negativos(analytics):
    serie = pd.DataFrame({
        "mesCriacao": pd.period_range("2024-01", periods=3, freq="M"),
        "quantidade": [2, -1, 4]
    })

    with pytest.raises(ValueError, match="valores negativos"):
        analytics.prever(serie)


def test_prever_rejeita_valores_nao_finitos(analytics):
    serie = pd.DataFrame({
        "mesCriacao": pd.period_range("2024-01", periods=3, freq="M"),
        "quantidade": [2, np.inf, 4]
    })

    with pytest.raises(ValueError, match="ausentes ou infinitos"):
        analytics.prever(serie)


def test_prever_rejeita_historico_insuficiente(analytics):
    serie = pd.DataFrame({
        "mesCriacao": pd.period_range("2024-01", periods=7, freq="M"),
        "quantidade": range(7)
    })

    with pytest.raises(ValueError, match="ao menos dois meses para treinamento"):
        analytics.prever(serie)


def test_prever_rejeita_horizonte_invalido(analytics, serie_mensal):
    with pytest.raises(ValueError, match="horizonte deve ser maior ou igual"):
        analytics.prever(serie_mensal, coluna_valor="novosUsuarios", horizonte=0)


def test_projecoes_nao_sao_negativas(analytics):
    serie = pd.DataFrame({
        "mesCriacao": pd.period_range("2024-01", periods=12, freq="M"),
        "quantidade": [12, 10, 8, 6, 4, 2, 1, 0, 0, 0, 0, 0]
    })

    resultado = analytics.prever(serie, quantidade_teste=3)

    assert (resultado["projecoes"]["quantidadePrevista"] >= 0).all()
    assert (resultado["projecoes"]["quantidadeEstimada"] >= 0).all()


def test_prever_rejeita_entrada_que_nao_seja_dataframe(analytics):
    with pytest.raises(TypeError, match="DataFrame"):
        analytics.prever(
            serie_mensal=[{"mesCriacao": "2025-01-01", "quantidade": 10}]
        )


@pytest.mark.parametrize(
    ("parametro", "valor"),
    [
        ("coluna_periodo", ""),
        ("coluna_valor", ""),
        ("coluna_periodo", None),
        ("coluna_valor", None),
    ],
)
def test_prever_rejeita_nomes_de_colunas_invalidos(
    analytics, serie_mensal, parametro, valor
):
    parametros = {
        "serie_mensal": serie_mensal,
        "horizonte": 3,
        "quantidade_teste": 2,
    }
    parametros[parametro] = valor

    with pytest.raises(TypeError):
        analytics.prever(**parametros)


def test_prever_rejeita_colunas_com_nomes_iguais(
    analytics, serie_mensal
):
    with pytest.raises(ValueError, match="devem ser diferentes"):
        analytics.prever(
            serie_mensal=serie_mensal,
            coluna_periodo="mesCriacao",
            coluna_valor="mesCriacao",
        )


@pytest.mark.parametrize("horizonte", [True, 1.5, "3"])
def test_prever_rejeita_horizonte_com_tipo_invalido(
    analytics, serie_mensal, horizonte
):
    with pytest.raises(TypeError):
        analytics.prever(
            serie_mensal=serie_mensal,
            horizonte=horizonte,
        )


@pytest.mark.parametrize("quantidade_teste", [True, 1.5, "2"])
def test_prever_rejeita_quantidade_teste_com_tipo_invalido(
    analytics, serie_mensal, quantidade_teste
):
    with pytest.raises(TypeError):
        analytics.prever(
            serie_mensal=serie_mensal,
            quantidade_teste=quantidade_teste,
        )


def test_prever_rejeita_quantidade_teste_menor_que_um(
    analytics, serie_mensal
):
    with pytest.raises(ValueError, match="maior ou igual a 1"):
        analytics.prever(
            serie_mensal=serie_mensal,
            quantidade_teste=0,
        )
