"""Testes unitários da classe AnuncioAnalytics."""


import pytest
import numpy as np
import pandas as pd

from app.analytics.anuncio_analytics import AnuncioAnalytics
from app.enums.tipo_negociacao import TipoNegociacao


@pytest.fixture
def anuncios():
    return [
        {
            "id": "A1",
            "uidUsuario": "U1",
            "uidLivro": "L1",
            "autores": ["J. K. Rowling"],
            "categorias": ["Fantasia", "Aventura"],
            "tipoNegociacao": "TROCA",
            "dataCriacao": "2026-08-05"
        },
        {
            "id": "A2",
            "uidUsuario": "U2",
            "uidLivro": "L2",
            "autores": ["George Orwell"],
            "categorias": ["Ficção"],
            "tipoNegociacao": "VENDA",
            "dataCriacao": "2026-08-10"
        },
        {
            "id": "A3",
            "uidUsuario": "U1",
            "uidLivro": "L3",
            "autores": ["J. K. Rowling"],
            "categorias": ["Fantasia"],
            "tipoNegociacao": "AMBOS",
            "dataCriacao": "2026-09-02"
        },
        {
            "id": "A4",
            "uidUsuario": "U3",
            "uidLivro": "L4",
            "autores": ["Machado de Assis"],
            "categorias": ["Romance"],
            "tipoNegociacao": "VENDA",
            "dataCriacao": "2026-09-10"
        },
        {
            "id": "A5",
            "uidUsuario": "U2",
            "uidLivro": "L5",
            "autores": ["George Orwell"],
            "categorias": ["Ficção", "Drama"],
            "tipoNegociacao": "TROCA",
            "dataCriacao": "2026-10-03"
        },
        {
            "id": "A6",
            "uidUsuario": "U4",
            "uidLivro": "L6",
            "autores": ["Clarice Lispector"],
            "categorias": ["Romance"],
            "tipoNegociacao": "AMBOS",
            "dataCriacao": "2026-10-08"
        }
    ]

@pytest.fixture
def analytics():
    return AnuncioAnalytics()

@pytest.fixture
def anuncios_incompletos():
    return [
        {
            "id": "A1",
            "uidUsuario": "U1",
            "uidLivro": "L1",
            "autores": [],
            "categorias": [],
            "tipoNegociacao": None,
            "dataCriacao": None
        },
        {
            "id": "A2",
            "uidUsuario": "U2",
            "uidLivro": "L2",
            "autores": ["George Orwell"],
            "categorias": ["Ficção"],
            "tipoNegociacao": "VENDA",
            "dataCriacao": "data-invalida"
        }
    ]

def test_deve_analisar_anuncios(anuncios, analytics):
    resultado = analytics.analisar(anuncios)

    assert resultado is not None
    assert resultado["geral"]["totalAnuncios"] == 6

def test_deve_calcular_indicadores_gerais(anuncios, analytics):
    resultado = analytics.analisar(anuncios)
    geral = resultado["geral"]

    assert geral["totalAnuncios"] == 6
    assert geral["totalUsuariosAnunciantes"] == 4
    assert geral["totalLivros"] == 6

    assert geral["anunciosSemAutores"] == 0
    assert geral["anunciosSemCategorias"] == 0
    assert geral["anunciosSemTipoNegociacao"] == 0
    assert geral["anunciosComDataInvalida"] == 0

    assert geral["quantidadeMesesAnalisados"] == 3


def test_deve_calcular_distribuicao_por_tipo(anuncios, analytics):
    resultado = analytics.analisar(anuncios)
    por_tipo = resultado["porTipo"].set_index("tipoNegociacao")

    assert por_tipo.loc["TROCA", "quantidadeAnuncios"] == 2
    assert por_tipo.loc["VENDA", "quantidadeAnuncios"] == 2
    assert por_tipo.loc["AMBOS", "quantidadeAnuncios"] == 2

    assert np.isclose(por_tipo["percentual"].sum(), 100.0, atol=0.01)


def test_deve_calcular_distribuicao_por_autor(anuncios, analytics):
    resultado = analytics.analisar(anuncios)
    por_autor = resultado["porAutor"].set_index("autor")

    assert por_autor.loc["J. K. Rowling", "quantidadeAnuncios"] == 2
    assert por_autor.loc["George Orwell", "quantidadeAnuncios"] == 2
    assert por_autor.loc["Machado de Assis", "quantidadeAnuncios"] == 1
    assert por_autor.loc["Clarice Lispector", "quantidadeAnuncios"] == 1

    assert np.isclose(
        por_autor["percentualAnuncios"].sum(),
        100.0,
        atol=0.01
    )

def test_deve_calcular_distribuicao_por_categoria(anuncios, analytics):
    resultado = analytics.analisar(anuncios)
    por_categoria = resultado["porCategoria"].set_index("categoria")

    assert por_categoria.loc["Fantasia", "quantidadeAnuncios"] == 2
    assert por_categoria.loc["Ficção", "quantidadeAnuncios"] == 2
    assert por_categoria.loc["Romance", "quantidadeAnuncios"] == 2
    assert por_categoria.loc["Aventura", "quantidadeAnuncios"] == 1
    assert por_categoria.loc["Drama", "quantidadeAnuncios"] == 1

    assert np.isclose(
        por_categoria["percentualAnuncios"].sum(),
        133.33,
        atol=0.01
    )


def test_deve_calcular_categoria_por_tipo(anuncios, analytics):
    resultado = analytics.analisar(anuncios)
    quantidades = resultado["categoriaPorTipo"]["quantidades"]

    assert quantidades.loc["Fantasia", "TROCA"] == 1
    assert quantidades.loc["Fantasia", "AMBOS"] == 1

    assert quantidades.loc["Ficção", "VENDA"] == 1
    assert quantidades.loc["Ficção", "TROCA"] == 1

    assert quantidades.loc["Romance", "VENDA"] == 1
    assert quantidades.loc["Romance", "AMBOS"] == 1

def test_deve_calcular_analise_temporal(anuncios, analytics):
    resultado = analytics.analisar(anuncios)
    anuncios_por_mes = resultado["temporal"]["anunciosPorMes"]

    assert len(anuncios_por_mes) == 3

    assert anuncios_por_mes.iloc[0]["mesCriacao"] == pd.Period("2026-08", freq="M")
    assert anuncios_por_mes.iloc[1]["mesCriacao"] == pd.Period("2026-09", freq="M")
    assert anuncios_por_mes.iloc[2]["mesCriacao"] == pd.Period("2026-10", freq="M")

    assert anuncios_por_mes.iloc[0]["novosAnuncios"] == 2
    assert anuncios_por_mes.iloc[1]["novosAnuncios"] == 2
    assert anuncios_por_mes.iloc[2]["novosAnuncios"] == 2

    assert anuncios_por_mes.iloc[1]["variacaoPercentual"] == 0.0
    assert anuncios_por_mes.iloc[2]["variacaoPercentual"] == 0.0


def test_deve_calcular_resumo_mensal(anuncios, analytics):
    resultado = analytics.analisar(anuncios)
    resumo = resultado["temporal"]["resumoMensal"]

    assert resumo["quantidadeMeses"] == 3
    assert resumo["menorQuantidade"] == 2
    assert resumo["maiorQuantidade"] == 2
    assert resumo["mediaMensal"] == 2.0

    assert resumo["maiorCrescimento"] is None
    assert resumo["maiorReducao"] is None

def test_deve_calcular_anuncios_por_mes_e_tipo(anuncios, analytics):
    resultado = analytics.analisar(anuncios)
    por_mes_tipo = resultado["temporal"]["anunciosPorMesTipo"]

    assert len(por_mes_tipo) == 6

    agosto = por_mes_tipo[por_mes_tipo["mesCriacao"] == pd.Period("2026-08", freq="M")]
    setembro = por_mes_tipo[por_mes_tipo["mesCriacao"] == pd.Period("2026-09", freq="M")]
    outubro = por_mes_tipo[por_mes_tipo["mesCriacao"] == pd.Period("2026-10", freq="M")]

    assert agosto["quantidadeAnuncios"].sum() == 2
    assert setembro["quantidadeAnuncios"].sum() == 2
    assert outubro["quantidadeAnuncios"].sum() == 2

    assert set(agosto["tipoNegociacao"]) == {"TROCA", "VENDA"}
    assert set(setembro["tipoNegociacao"]) == {"AMBOS", "VENDA"}
    assert set(outubro["tipoNegociacao"]) == {"AMBOS", "TROCA"}

def test_deve_calcular_evolucao_por_tipo(anuncios, analytics):
    resultado = analytics.analisar(anuncios)
    evolucao = resultado["temporal"]["evolucaoPorTipo"]

    agosto = pd.Period("2026-08", freq="M")
    setembro = pd.Period("2026-09", freq="M")
    outubro = pd.Period("2026-10", freq="M")

    assert list(evolucao.columns) == ["TROCA", "VENDA", "AMBOS"]

    assert evolucao.loc[agosto, "TROCA"] == 1
    assert evolucao.loc[agosto, "VENDA"] == 1
    assert evolucao.loc[agosto, "AMBOS"] == 0

    assert evolucao.loc[setembro, "TROCA"] == 0
    assert evolucao.loc[setembro, "VENDA"] == 1
    assert evolucao.loc[setembro, "AMBOS"] == 1

    assert evolucao.loc[outubro, "TROCA"] == 1
    assert evolucao.loc[outubro, "VENDA"] == 0
    assert evolucao.loc[outubro, "AMBOS"] == 1

def test_deve_gerar_insights(anuncios, analytics):
    resultado = analytics.analisar(anuncios)
    insights = resultado["insights"]

    assert isinstance(insights, list)
    assert len(insights) == 3

    assert any(
        "A categoria com maior presença é" in insight
        for insight in insights
    )

    assert any(
        "A modalidade mais frequente é" in insight
        for insight in insights
    )

    assert any(
        "Foram analisados 6 anúncios" in insight
        for insight in insights
    )

def test_deve_retornar_estrutura_vazia_sem_anuncios(analytics):
    resultado = analytics.analisar([])

    assert resultado["geral"]["totalAnuncios"] == 0
    assert resultado["geral"]["totalUsuariosAnunciantes"] == 0
    assert resultado["geral"]["totalLivros"] == 0

    assert resultado["porTipo"].empty
    assert resultado["porAutor"].empty
    assert resultado["porCategoria"].empty

    assert resultado["categoriaPorTipo"]["quantidades"].empty
    assert resultado["categoriaPorTipo"]["percentuais"].empty

    assert resultado["temporal"]["anunciosPorMes"].empty
    assert resultado["temporal"]["anunciosPorMesTipo"].empty
    assert resultado["temporal"]["evolucaoPorTipo"].empty

    assert resultado["insights"] == []

def test_deve_identificar_dados_incompletos(anuncios_incompletos, analytics):
    resultado = analytics.analisar(anuncios_incompletos)
    geral = resultado["geral"]

    assert geral["totalAnuncios"] == 2
    assert geral["anunciosSemAutores"] == 1
    assert geral["anunciosSemCategorias"] == 1
    assert geral["anunciosSemTipoNegociacao"] == 1
    assert geral["anunciosComDataInvalida"] == 2
    assert geral["quantidadeMesesAnalisados"] == 0


def test_deve_retornar_estrutura_vazia_quando_anuncios_for_none(analytics):
    resultado = analytics.analisar(None)

    assert resultado["geral"]["totalAnuncios"] == 0
    assert resultado["geral"]["totalUsuariosAnunciantes"] == 0
    assert resultado["geral"]["totalLivros"] == 0

    assert resultado["porTipo"].empty
    assert resultado["porAutor"].empty
    assert resultado["porCategoria"].empty

    assert resultado["temporal"]["anunciosPorMes"].empty
    assert resultado["insights"] == []

def test_deve_normalizar_tipos_de_negociacao(anuncios, analytics):
    anuncios_teste = [
        {**anuncios[0], "tipoNegociacao": " troca "},
        {**anuncios[1], "tipoNegociacao": "venda"},
        {**anuncios[2], "tipoNegociacao": " Ambos "}
    ]

    resultado = analytics.analisar(anuncios_teste)
    por_tipo = resultado["porTipo"].set_index("tipoNegociacao")

    assert por_tipo.loc["TROCA", "quantidadeAnuncios"] == 1
    assert por_tipo.loc["VENDA", "quantidadeAnuncios"] == 1
    assert por_tipo.loc["AMBOS", "quantidadeAnuncios"] == 1

def test_deve_normalizar_tipo_de_negociacao_enum(analytics):
    anuncios_teste = [
        {
            "id": "A1",
            "uidUsuario": "U1",
            "uidLivro": "L1",
            "autores": ["Autor 1"],
            "categorias": ["Fantasia"],
            "tipoNegociacao": TipoNegociacao.TROCA,
            "dataCriacao": "2026-08-05"
        }
    ]

    resultado = analytics.analisar(anuncios_teste)
    por_tipo = resultado["porTipo"].set_index("tipoNegociacao")

    assert por_tipo.loc["TROCA", "quantidadeAnuncios"] == 1
