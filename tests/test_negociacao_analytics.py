from datetime import datetime

import numpy as np

from app.analytics.negociacao_analytics import NegociacaoAnalytics
from app.enums.status_negociacao import StatusNegociacao
from app.enums.tipo_negociacao import TipoNegociacao
from app.models.negociacao import Negociacao




def criar_negociacoes():
    return [
        Negociacao(
            id="N1",
            anuncioId="A1",
            anuncioOferecidoId="A2",
            categoriasAnuncio=["Fantasia", "Aventura"],
            categoriasAnuncioOferecido=["Fantasia", "Aventura"],
            dataNegociacao=datetime(2026, 8, 5),
            dataFinalizacao=datetime(2026, 8, 10),
            tipoNegociacao=TipoNegociacao.TROCA,
            status=StatusNegociacao.FINALIZADA
        ),
        Negociacao(
            id="N2",
            anuncioId="A3",
            anuncioOferecidoId="A4",
            categoriasAnuncio=["Fantasia"],
            categoriasAnuncioOferecido=["Fantasia", "Aventura"],
            dataNegociacao=datetime(2026, 8, 15),
            dataFinalizacao=None,
            tipoNegociacao=TipoNegociacao.TROCA,
            status=StatusNegociacao.EM_ANDAMENTO
        ),
        Negociacao(
            id="N3",
            anuncioId="A5",
            anuncioOferecidoId="A6",
            categoriasAnuncio=["Tecnologia"],
            categoriasAnuncioOferecido=["Romance"],
            dataNegociacao=datetime(2026, 9, 2),
            dataFinalizacao=datetime(2026, 9, 12),
            tipoNegociacao=TipoNegociacao.TROCA,
            status=StatusNegociacao.FINALIZADA
        ),
        Negociacao(
            id="N4",
            anuncioId="A7",
            anuncioOferecidoId=None,
            categoriasAnuncio=["Romance"],
            categoriasAnuncioOferecido=None,
            dataNegociacao=datetime(2026, 9, 10),
            dataFinalizacao=datetime(2026, 9, 14),
            tipoNegociacao=TipoNegociacao.VENDA,
            status=StatusNegociacao.FINALIZADA
        ),
        Negociacao(
            id="N5",
            anuncioId="A8",
            anuncioOferecidoId=None,
            categoriasAnuncio=["Tecnologia"],
            categoriasAnuncioOferecido=None,
            dataNegociacao=datetime(2026, 10, 3),
            dataFinalizacao=None,
            tipoNegociacao=TipoNegociacao.VENDA,
            status=StatusNegociacao.PENDENTE
        ),
        Negociacao(
            id="N6",
            anuncioId="A9",
            anuncioOferecidoId=None,
            categoriasAnuncio=["Fantasia"],
            categoriasAnuncioOferecido=None,
            dataNegociacao=datetime(2026, 10, 8),
            dataFinalizacao=datetime(2026, 10, 11),
            tipoNegociacao=TipoNegociacao.VENDA,
            status=StatusNegociacao.FINALIZADA
        )
    ]


def criar_negociacoes_nao_finalizadas():
    return [
        Negociacao(
            id="N7",
            anuncioId="A10",
            anuncioOferecidoId=None,
            categoriasAnuncio=["Fantasia"],
            categoriasAnuncioOferecido=None,
            dataNegociacao=datetime(2026, 10, 12),
            dataFinalizacao=None,
            tipoNegociacao=TipoNegociacao.VENDA,
            status=StatusNegociacao.PENDENTE
        ),
        Negociacao(
            id="N8",
            anuncioId="A11",
            anuncioOferecidoId="A12",
            categoriasAnuncio=["Tecnologia"],
            categoriasAnuncioOferecido=["Romance"],
            dataNegociacao=datetime(2026, 10, 13),
            dataFinalizacao=None,
            tipoNegociacao=TipoNegociacao.TROCA,
            status=StatusNegociacao.EM_ANDAMENTO
        )
    ]

def test_deve_analisar_negociacoes():
    analytics = NegociacaoAnalytics()

    resultado = analytics.analisar(
        criar_negociacoes()
    )

    assert resultado is not None
    assert resultado["geral"]["totalNegociacoes"] == 6


def test_deve_calcular_negociacoes_por_tipo():
    analytics = NegociacaoAnalytics()

    resultado = analytics.analisar(
        criar_negociacoes()
    )

    analise_por_tipo = resultado["porTipo"]

    troca = analise_por_tipo[
        analise_por_tipo["tipoNegociacao"] == "TROCA"
    ].iloc[0]

    venda = analise_por_tipo[
        analise_por_tipo["tipoNegociacao"] == "VENDA"
    ].iloc[0]

    assert troca["totalNegociacoes"] == 3
    assert venda["totalNegociacoes"] == 3


def test_deve_calcular_taxa_finalizacao_por_tipo():
    analytics = NegociacaoAnalytics()

    resultado = analytics.analisar(
        criar_negociacoes()
    )

    analise_por_tipo = resultado["porTipo"]

    troca = analise_por_tipo[
        analise_por_tipo["tipoNegociacao"] == "TROCA"
    ].iloc[0]

    venda = analise_por_tipo[
        analise_por_tipo["tipoNegociacao"] == "VENDA"
    ].iloc[0]

    assert troca["totalFinalizadas"] == 2
    assert venda["totalFinalizadas"] == 2

    assert troca["taxaFinalizacao"] == 2 / 3
    assert venda["taxaFinalizacao"] == 2 / 3

def test_deve_calcular_negociacoes_por_categoria():
    analytics = NegociacaoAnalytics()

    resultado = analytics.analisar(
        criar_negociacoes()
    )

    analise_por_categoria = resultado["porCategoria"]

    fantasia = analise_por_categoria[
        analise_por_categoria["categoria"] == "Fantasia"
    ].iloc[0]

    aventura = analise_por_categoria[
        analise_por_categoria["categoria"] == "Aventura"
    ].iloc[0]

    tecnologia = analise_por_categoria[
        analise_por_categoria["categoria"] == "Tecnologia"
    ].iloc[0]

    romance = analise_por_categoria[
        analise_por_categoria["categoria"] == "Romance"
    ].iloc[0]

    assert fantasia["totalNegociacoes"] == 3
    assert fantasia["totalFinalizadas"] == 2
    assert fantasia["taxaFinalizacao"] == 2 / 3

    assert aventura["totalNegociacoes"] == 1
    assert aventura["totalFinalizadas"] == 1
    assert aventura["taxaFinalizacao"] == 1

    assert tecnologia["totalNegociacoes"] == 2
    assert tecnologia["totalFinalizadas"] == 1
    assert tecnologia["taxaFinalizacao"] == 1 / 2

    assert romance["totalNegociacoes"] == 1
    assert romance["totalFinalizadas"] == 1
    assert romance["taxaFinalizacao"] == 1

def test_deve_analisar_afinidade_das_categorias():
    analytics = NegociacaoAnalytics()

    resultado = analytics.analisar(
        criar_negociacoes()
    )

    analise_afinidade = resultado["afinidadeCategorias"]

    mesma = analise_afinidade[
        analise_afinidade["afinidade"] == "MESMA"
    ].iloc[0]

    semelhante = analise_afinidade[
        analise_afinidade["afinidade"] == "SEMELHANTE"
    ].iloc[0]

    diferente = analise_afinidade[
        analise_afinidade["afinidade"] == "DIFERENTE"
    ].iloc[0]

    assert mesma["totalNegociacoes"] == 1
    assert mesma["totalFinalizadas"] == 1
    assert mesma["taxaFinalizacao"] == 1

    assert semelhante["totalNegociacoes"] == 1
    assert semelhante["totalFinalizadas"] == 0
    assert semelhante["taxaFinalizacao"] == 0

    assert diferente["totalNegociacoes"] == 1
    assert diferente["totalFinalizadas"] == 1
    assert diferente["taxaFinalizacao"] == 1


def test_deve_analisar_combinacoes_de_categorias():
    analytics = NegociacaoAnalytics()

    resultado = analytics.analisar(
        criar_negociacoes()
    )

    analise_combinacoes = resultado["combinacoesCategorias"]

    fantasia_fantasia = analise_combinacoes[
        (analise_combinacoes["categoriaAnuncio"] == "Fantasia")
        & (
            analise_combinacoes["categoriaAnuncioOferecido"]
            == "Fantasia"
        )
    ].iloc[0]

    fantasia_aventura = analise_combinacoes[
        (analise_combinacoes["categoriaAnuncio"] == "Fantasia")
        & (
            analise_combinacoes["categoriaAnuncioOferecido"]
            == "Aventura"
        )
    ].iloc[0]

    tecnologia_romance = analise_combinacoes[
        (analise_combinacoes["categoriaAnuncio"] == "Tecnologia")
        & (
            analise_combinacoes["categoriaAnuncioOferecido"]
            == "Romance"
        )
    ].iloc[0]

    assert fantasia_fantasia["totalNegociacoes"] == 2
    assert fantasia_fantasia["totalFinalizadas"] == 1
    assert fantasia_fantasia["taxaFinalizacao"] == 1 / 2

    assert fantasia_aventura["totalNegociacoes"] == 2
    assert fantasia_aventura["totalFinalizadas"] == 1
    assert fantasia_aventura["taxaFinalizacao"] == 1 / 2

    assert tecnologia_romance["totalNegociacoes"] == 1
    assert tecnologia_romance["totalFinalizadas"] == 1
    assert tecnologia_romance["taxaFinalizacao"] == 1

def test_deve_analisar_negociacoes_por_mes():
    analytics = NegociacaoAnalytics()

    resultado = analytics.analisar(
        criar_negociacoes()
    )

    negociacoes_por_mes = resultado["temporal"]["negociacoesPorMes"]

    agosto = negociacoes_por_mes[
        negociacoes_por_mes["mesNegociacao"] == "2026-08"
    ].iloc[0]

    setembro = negociacoes_por_mes[
        negociacoes_por_mes["mesNegociacao"] == "2026-09"
    ].iloc[0]

    outubro = negociacoes_por_mes[
        negociacoes_por_mes["mesNegociacao"] == "2026-10"
    ].iloc[0]

    assert agosto["quantidade"] == 2
    assert setembro["quantidade"] == 2
    assert outubro["quantidade"] == 2

def test_deve_analisar_finalizacoes_por_mes():
    analytics = NegociacaoAnalytics()

    resultado = analytics.analisar(
        criar_negociacoes()
    )

    finalizacoes_por_mes = resultado["temporal"]["finalizacoesPorMes"]

    agosto = finalizacoes_por_mes[
        finalizacoes_por_mes["mesFinalizacao"] == "2026-08"
    ].iloc[0]

    setembro = finalizacoes_por_mes[
        finalizacoes_por_mes["mesFinalizacao"] == "2026-09"
    ].iloc[0]

    outubro = finalizacoes_por_mes[
        finalizacoes_por_mes["mesFinalizacao"] == "2026-10"
    ].iloc[0]

    assert agosto["quantidade"] == 1
    assert setembro["quantidade"] == 2
    assert outubro["quantidade"] == 1


def test_deve_calcular_tempo_medio_finalizacao():
    analytics = NegociacaoAnalytics()

    resultado = analytics.analisar(
        criar_negociacoes()
    )

    tempo_finalizacao = resultado["temporal"]["tempoFinalizacao"]

    troca = tempo_finalizacao[
        tempo_finalizacao["tipoNegociacao"] == "TROCA"
    ].iloc[0]

    venda = tempo_finalizacao[
        tempo_finalizacao["tipoNegociacao"] == "VENDA"
    ].iloc[0]

    assert troca["totalFinalizadas"] == 2
    assert troca["tempoMedioDias"] == 7.5

    assert venda["totalFinalizadas"] == 2
    assert venda["tempoMedioDias"] == 3.5


def test_deve_calcular_taxa_finalizacao_por_mes_inicio():
    analytics = NegociacaoAnalytics()

    resultado = analytics.analisar(
        criar_negociacoes()
    )

    taxa_por_mes = resultado["temporal"]["taxaFinalizacaoPorMesInicio"]

    agosto = taxa_por_mes[
        taxa_por_mes["mesNegociacao"] == "2026-08"
    ].iloc[0]

    setembro = taxa_por_mes[
        taxa_por_mes["mesNegociacao"] == "2026-09"
    ].iloc[0]

    outubro = taxa_por_mes[
        taxa_por_mes["mesNegociacao"] == "2026-10"
    ].iloc[0]

    assert agosto["totalNegociacoes"] == 2
    assert agosto["totalFinalizadas"] == 1
    assert agosto["taxaFinalizacao"] == 0.5

    assert setembro["totalNegociacoes"] == 2
    assert setembro["totalFinalizadas"] == 2
    assert setembro["taxaFinalizacao"] == 1.0

    assert outubro["totalNegociacoes"] == 2
    assert outubro["totalFinalizadas"] == 1
    assert outubro["taxaFinalizacao"] == 0.5


def test_deve_ajustar_taxa_finalizacao_por_categoria():
    analytics = NegociacaoAnalytics()

    resultado = analytics.analisar(
        criar_negociacoes()
    )

    analise_por_categoria = resultado["porCategoria"]

    assert "taxaFinalizacaoAjustada" in analise_por_categoria.columns
    assert analise_por_categoria["taxaFinalizacaoAjustada"].notna().all()

    assert (
        (analise_por_categoria["taxaFinalizacaoAjustada"] >= 0)
        & (analise_por_categoria["taxaFinalizacaoAjustada"] <= 1)
    ).all()

def test_deve_ajustar_taxa_finalizacao_por_combinacao():
    analytics = NegociacaoAnalytics()

    resultado = analytics.analisar(
        criar_negociacoes()
    )

    analise_combinacoes = resultado["combinacoesCategorias"]

    assert "taxaFinalizacaoAjustada" in analise_combinacoes.columns
    assert analise_combinacoes["taxaFinalizacaoAjustada"].notna().all()

    assert (
        (analise_combinacoes["taxaFinalizacaoAjustada"] >= 0)
        & (analise_combinacoes["taxaFinalizacaoAjustada"] <= 1)
    ).all()


def test_deve_gerar_insights():
    analytics = NegociacaoAnalytics()

    resultado = analytics.analisar(
        criar_negociacoes()
    )

    insights = resultado["insights"]

    assert insights is not None
    assert len(insights) > 0


def test_deve_gerar_insight_por_tipo_negociacao():
    analytics = NegociacaoAnalytics()

    resultado = analytics.analisar(
        criar_negociacoes()
    )

    insights = resultado["insights"]

    insight_tipo = next(
        (
            insight
            for insight in insights
            if insight["tipo"] == "TIPO_NEGOCIACAO"
        ),
        None
    )

    assert insight_tipo is not None


def test_deve_gerar_tipos_de_insights_esperados():
    analytics = NegociacaoAnalytics()

    resultado = analytics.analisar(
        criar_negociacoes()
    )

    tipos_insights = {
        insight["tipo"]
        for insight in resultado["insights"]
    }

    tipos_esperados = {
        "TIPO_NEGOCIACAO",
        "CATEGORIA",
        "TEMPO_FINALIZACAO",
        "EVOLUCAO_TEMPORAL",
        "AFINIDADE",
        "COMBINACAO_CATEGORIAS"
    }

    assert tipos_esperados.issubset(tipos_insights)

def test_deve_aceitar_lista_de_negociacoes_vazia():
    analytics = NegociacaoAnalytics()

    resultado = analytics.analisar([])

    assert resultado is not None
    assert resultado["geral"]["totalNegociacoes"] == 0
    assert resultado["insights"] == []

def test_deve_aceitar_negociacoes_sem_finalizacoes():
    analytics = NegociacaoAnalytics()

    resultado = analytics.analisar(
        criar_negociacoes_nao_finalizadas()
    )

    assert resultado["geral"]["totalNegociacoes"] == 2

    analise_por_tipo = resultado["porTipo"]

    assert (analise_por_tipo["totalFinalizadas"] == 0).all()
    assert (analise_por_tipo["taxaFinalizacao"] == 0).all()

    assert resultado["temporal"]["tempoFinalizacao"].empty

def test_deve_aceitar_negociacoes_sem_categorias():
    analytics = NegociacaoAnalytics()

    negociacao = Negociacao(
        id="N9",
        anuncioId="A13",
        anuncioOferecidoId=None,
        categoriasAnuncio=[],
        categoriasAnuncioOferecido=None,
        dataNegociacao=datetime(2026, 10, 15),
        dataFinalizacao=None,
        tipoNegociacao=TipoNegociacao.VENDA,
        status=StatusNegociacao.PENDENTE
    )

    resultado = analytics.analisar([negociacao])

    assert resultado["geral"]["totalNegociacoes"] == 1

def test_deve_analisar_negociacoes_com_categorias_parcialmente_ausentes():
    analytics = NegociacaoAnalytics()

    negociacao_valida = Negociacao(
        id="N10",
        anuncioId="A14",
        anuncioOferecidoId=None,
        categoriasAnuncio=["Fantasia"],
        categoriasAnuncioOferecido=None,
        dataNegociacao=datetime(2026, 10, 15),
        dataFinalizacao=None,
        tipoNegociacao=TipoNegociacao.VENDA,
        status=StatusNegociacao.PENDENTE
    )

    negociacao_sem_categorias = Negociacao(
        id="N11",
        anuncioId="A15",
        anuncioOferecidoId=None,
        categoriasAnuncio=[],
        categoriasAnuncioOferecido=None,
        dataNegociacao=datetime(2026, 10, 16),
        dataFinalizacao=None,
        tipoNegociacao=TipoNegociacao.VENDA,
        status=StatusNegociacao.PENDENTE
    )

    resultado = analytics.analisar([
        negociacao_valida,
        negociacao_sem_categorias
    ])

    assert resultado["geral"]["totalNegociacoes"] == 2

def test_deve_analisar_negociacoes_com_datas_de_finalizacao_mistas():
    analytics = NegociacaoAnalytics()

    negociacao_finalizada = Negociacao(
        id="N12",
        anuncioId="A16",
        anuncioOferecidoId=None,
        categoriasAnuncio=["Fantasia"],
        categoriasAnuncioOferecido=None,
        dataNegociacao=datetime(2026, 10, 10),
        dataFinalizacao=datetime(2026, 10, 15),
        tipoNegociacao=TipoNegociacao.VENDA,
        status=StatusNegociacao.FINALIZADA
    )

    negociacao_pendente = Negociacao(
        id="N13",
        anuncioId="A17",
        anuncioOferecidoId=None,
        categoriasAnuncio=["Tecnologia"],
        categoriasAnuncioOferecido=None,
        dataNegociacao=datetime(2026, 10, 16),
        dataFinalizacao=None,
        tipoNegociacao=TipoNegociacao.VENDA,
        status=StatusNegociacao.PENDENTE
    )

    resultado = analytics.analisar([
        negociacao_finalizada,
        negociacao_pendente
    ])

    assert resultado["geral"]["totalNegociacoes"] == 2

def test_deve_analisar_negociacoes_em_meses_diferentes():
    analytics = NegociacaoAnalytics()

    negociacoes = [
        Negociacao(
            id="N14",
            anuncioId="A18",
            anuncioOferecidoId=None,
            categoriasAnuncio=["Fantasia"],
            categoriasAnuncioOferecido=None,
            dataNegociacao=datetime(2026, 9, 15),
            dataFinalizacao=None,
            tipoNegociacao=TipoNegociacao.VENDA,
            status=StatusNegociacao.PENDENTE
        ),
        Negociacao(
            id="N15",
            anuncioId="A19",
            anuncioOferecidoId=None,
            categoriasAnuncio=["Tecnologia"],
            categoriasAnuncioOferecido=None,
            dataNegociacao=datetime(2026, 10, 15),
            dataFinalizacao=None,
            tipoNegociacao=TipoNegociacao.VENDA,
            status=StatusNegociacao.PENDENTE
        )
    ]

    resultado = analytics.analisar(negociacoes)

    assert resultado["geral"]["totalNegociacoes"] == 2
    assert len(resultado["temporal"]["negociacoesPorMes"]) == 2

def test_deve_ignorar_afinidade_quando_nao_ha_anuncio_oferecido():
    analytics = NegociacaoAnalytics()

    negociacao = Negociacao(
        id="N16",
        anuncioId="A20",
        anuncioOferecidoId=None,
        categoriasAnuncio=["Fantasia"],
        categoriasAnuncioOferecido=None,
        dataNegociacao=datetime(2026, 10, 20),
        dataFinalizacao=None,
        tipoNegociacao=TipoNegociacao.TROCA,
        status=StatusNegociacao.PENDENTE
    )

    resultado = analytics.analisar([negociacao])

    assert resultado["geral"]["totalNegociacoes"] == 1
    assert resultado["afinidadeCategorias"].empty

def test_deve_analisar_negociacao_com_multiplas_categorias():
    analytics = NegociacaoAnalytics()

    negociacao = Negociacao(
        id="N17",
        anuncioId="A21",
        anuncioOferecidoId=None,
        categoriasAnuncio=["Fantasia", "Aventura", "Ficção"],
        categoriasAnuncioOferecido=None,
        dataNegociacao=datetime(2026, 10, 21),
        dataFinalizacao=None,
        tipoNegociacao=TipoNegociacao.VENDA,
        status=StatusNegociacao.PENDENTE
    )

    resultado = analytics.analisar([negociacao])

    assert resultado["geral"]["totalNegociacoes"] == 1

    categorias = resultado["porCategoria"]["categoria"].tolist()

    assert set(categorias) == {"Fantasia", "Aventura", "Ficção"}

def test_deve_evitar_duplicidade_de_categoria_na_mesma_negociacao():
    analytics = NegociacaoAnalytics()

    negociacao = Negociacao(
        id="N18",
        anuncioId="A22",
        anuncioOferecidoId=None,
        categoriasAnuncio=["Fantasia", "Fantasia", "Aventura"],
        categoriasAnuncioOferecido=None,
        dataNegociacao=datetime(2026, 10, 22),
        dataFinalizacao=None,
        tipoNegociacao=TipoNegociacao.VENDA,
        status=StatusNegociacao.PENDENTE
    )

    resultado = analytics.analisar([negociacao])

    categorias = resultado["porCategoria"]

    fantasia = categorias[categorias["categoria"] == "Fantasia"]

    assert resultado["geral"]["totalNegociacoes"] == 1
    assert len(fantasia) == 1
    assert fantasia.iloc[0]["totalNegociacoes"] == 1


def test_deve_tratar_data_de_finalizacao_anterior_a_negociacao():
    analytics = NegociacaoAnalytics()

    negociacao = Negociacao(
        id="N19",
        anuncioId="A23",
        anuncioOferecidoId=None,
        categoriasAnuncio=["Fantasia"],
        categoriasAnuncioOferecido=None,
        dataNegociacao=datetime(2026, 10, 22),
        dataFinalizacao=datetime(2026, 10, 20),
        tipoNegociacao=TipoNegociacao.VENDA,
        status=StatusNegociacao.FINALIZADA
    )

    resultado = analytics.analisar([negociacao])

    tempo_medio = resultado["temporal"]["tempoFinalizacao"]

    assert (
        tempo_medio.empty
        or (tempo_medio["tempoMedioDias"] >= 0).all()
    )


def test_deve_ignorar_finalizacao_sem_data_finalizacao():
    analytics = NegociacaoAnalytics()

    negociacao = Negociacao(
        id="N20",
        anuncioId="A24",
        anuncioOferecidoId=None,
        categoriasAnuncio=["Fantasia"],
        categoriasAnuncioOferecido=None,
        dataNegociacao=datetime(2026, 10, 22),
        dataFinalizacao=None,
        tipoNegociacao=TipoNegociacao.VENDA,
        status=StatusNegociacao.FINALIZADA
    )

    resultado = analytics.analisar([negociacao])

    tempo_medio = resultado["temporal"]["tempoFinalizacao"]

    assert (
        tempo_medio.empty
        or (tempo_medio["tempoMedioDias"] >= 0).all()
    )

def test_deve_calcular_tempo_medio_ignorando_datas_invalidas():
    analytics = NegociacaoAnalytics()

    negociacao_valida = Negociacao(
        id="N22",
        anuncioId="A26",
        anuncioOferecidoId=None,
        categoriasAnuncio=["Fantasia"],
        categoriasAnuncioOferecido=None,
        dataNegociacao=datetime(2026, 10, 20),
        dataFinalizacao=datetime(2026, 10, 23),
        tipoNegociacao=TipoNegociacao.VENDA,
        status=StatusNegociacao.FINALIZADA
    )

    negociacao_sem_data_finalizacao = Negociacao(
        id="N23",
        anuncioId="A27",
        anuncioOferecidoId=None,
        categoriasAnuncio=["Aventura"],
        categoriasAnuncioOferecido=None,
        dataNegociacao=datetime(2026, 10, 21),
        dataFinalizacao=None,
        tipoNegociacao=TipoNegociacao.VENDA,
        status=StatusNegociacao.FINALIZADA
    )

    resultado = analytics.analisar([
        negociacao_valida,
        negociacao_sem_data_finalizacao
    ])

    tempo_finalizacao = resultado["temporal"]["tempoFinalizacao"]

    assert not tempo_finalizacao.empty
    assert tempo_finalizacao["tempoMedioDias"].iloc[0] == 3.0

def test_deve_calcular_tempo_medio_separadamente_por_tipo():
    analytics = NegociacaoAnalytics()

    venda = Negociacao(
        id="N24",
        anuncioId="A28",
        anuncioOferecidoId=None,
        categoriasAnuncio=["Fantasia"],
        categoriasAnuncioOferecido=None,
        dataNegociacao=datetime(2026, 10, 20),
        dataFinalizacao=datetime(2026, 10, 22),
        tipoNegociacao=TipoNegociacao.VENDA,
        status=StatusNegociacao.FINALIZADA
    )

    troca = Negociacao(
        id="N25",
        anuncioId="A29",
        anuncioOferecidoId="A30",
        categoriasAnuncio=["Aventura"],
        categoriasAnuncioOferecido=["Ficção científica"],
        dataNegociacao=datetime(2026, 10, 20),
        dataFinalizacao=datetime(2026, 10, 25),
        tipoNegociacao=TipoNegociacao.TROCA,
        status=StatusNegociacao.FINALIZADA
    )

    resultado = analytics.analisar([venda, troca])
    tempo_finalizacao = resultado["temporal"]["tempoFinalizacao"]

    tempos = tempo_finalizacao.set_index("tipoNegociacao")["tempoMedioDias"]

    assert tempos[TipoNegociacao.VENDA.value] == 2.0
    assert tempos[TipoNegociacao.TROCA.value] == 5.0

def test_deve_ignorar_data_finalizacao_de_negociacao_nao_finalizada():
    analytics = NegociacaoAnalytics()

    negociacao = Negociacao(
        id="N26",
        anuncioId="A31",
        anuncioOferecidoId=None,
        categoriasAnuncio=["Fantasia"],
        categoriasAnuncioOferecido=None,
        dataNegociacao=datetime(2026, 10, 20),
        dataFinalizacao=datetime(2026, 10, 23),
        tipoNegociacao=TipoNegociacao.VENDA,
        status=StatusNegociacao.PENDENTE
    )

    resultado = analytics.analisar([negociacao])
    tempo_finalizacao = resultado["temporal"]["tempoFinalizacao"]

    assert tempo_finalizacao.empty

def test_deve_rejeitar_estimativa_com_menos_de_dois_grupos():
    import pandas as pd
    import pytest

    analytics = NegociacaoAnalytics()

    indicadores = pd.DataFrame([
        {
            "totalFinalizadas": 1,
            "totalNegociacoes": 2
        }
    ])

    with pytest.raises(
        ValueError,
        match="pelo menos dois grupos"
    ):
        analytics._estimar_parametros_beta_binomial(indicadores)


def test_deve_lancar_erro_quando_otimizacao_beta_binomial_falhar(monkeypatch):
    from types import SimpleNamespace
    import pandas as pd
    import pytest
    import app.analytics.negociacao_analytics as modulo_analytics

    analytics = NegociacaoAnalytics()

    indicadores = pd.DataFrame([
        {"totalFinalizadas": 1, "totalNegociacoes": 2},
        {"totalFinalizadas": 2, "totalNegociacoes": 3},
    ])

    def minimizar_falha(*args, **kwargs):
        return SimpleNamespace(success=False)

    monkeypatch.setattr(modulo_analytics, "minimize", minimizar_falha)

    with pytest.raises(
        ValueError,
        match="Não foi possível estimar os parâmetros Beta-Binomial"
    ):
        analytics._estimar_parametros_beta_binomial(indicadores)


def test_deve_gerar_insight_quando_taxas_de_troca_e_venda_fore_m_iguais():
    import pandas as pd

    analytics = NegociacaoAnalytics()

    analise_por_tipo = pd.DataFrame([
        {
            "tipoNegociacao": "TROCA",
            "totalNegociacoes": 10,
            "totalFinalizadas": 5,
            "taxaFinalizacao": 0.5
        },
        {
            "tipoNegociacao": "VENDA",
            "totalNegociacoes": 20,
            "totalFinalizadas": 10,
            "taxaFinalizacao": 0.5
        }
    ])

    insight = analytics._gerar_insight_tipo_negociacao(
        analise_por_tipo
    )

    assert insight is not None
    assert insight["dados"]["modalidadeDestaque"] == "EMPATE"
    assert insight["dados"]["taxaFinalizacaoTroca"] == 0.5
    assert insight["dados"]["taxaFinalizacaoVenda"] == 0.5
    assert insight["dados"]["diferencaTaxaFinalizacao"] == 0.0

def test_deve_destacar_troca_quando_tiver_maior_taxa_de_finalizacao():
    import numpy as np
    import pandas as pd

    analytics = NegociacaoAnalytics()

    analise_por_tipo = pd.DataFrame([
        {
            "tipoNegociacao": "TROCA",
            "totalNegociacoes": 10,
            "totalFinalizadas": 8,
            "taxaFinalizacao": 0.8
        },
        {
            "tipoNegociacao": "VENDA",
            "totalNegociacoes": 20,
            "totalFinalizadas": 10,
            "taxaFinalizacao": 0.5
        }
    ])

    insight = analytics._gerar_insight_tipo_negociacao(
        analise_por_tipo
    )

    assert insight is not None
    assert insight["dados"]["modalidadeDestaque"] == "TROCA"
    assert np.isclose(insight["dados"]["taxaFinalizacaoTroca"], 0.8)
    assert np.isclose(insight["dados"]["taxaFinalizacaoVenda"], 0.5)
    assert np.isclose(insight["dados"]["diferencaTaxaFinalizacao"], 0.3)

def test_deve_destacar_venda_quando_tiver_maior_taxa_de_finalizacao():
    import numpy as np
    import pandas as pd

    analytics = NegociacaoAnalytics()

    analise_por_tipo = pd.DataFrame([
        {
            "tipoNegociacao": "TROCA",
            "totalNegociacoes": 10,
            "totalFinalizadas": 5,
            "taxaFinalizacao": 0.5
        },
        {
            "tipoNegociacao": "VENDA",
            "totalNegociacoes": 20,
            "totalFinalizadas": 16,
            "taxaFinalizacao": 0.8
        }
    ])

    insight = analytics._gerar_insight_tipo_negociacao(
        analise_por_tipo
    )

    assert insight is not None
    assert insight["dados"]["modalidadeDestaque"] == "VENDA"
    assert np.isclose(insight["dados"]["taxaFinalizacaoTroca"], 0.5)
    assert np.isclose(insight["dados"]["taxaFinalizacaoVenda"], 0.8)
    assert np.isclose(insight["dados"]["diferencaTaxaFinalizacao"], 0.3)

def test_deve_retornar_none_quando_houver_apenas_um_tipo_de_negociacao():
    import pandas as pd

    analytics = NegociacaoAnalytics()

    analise_por_tipo = pd.DataFrame([
        {
            "tipoNegociacao": "TROCA",
            "totalNegociacoes": 10,
            "totalFinalizadas": 8,
            "taxaFinalizacao": 0.8
        }
    ])

    insight = analytics._gerar_insight_tipo_negociacao(
        analise_por_tipo
    )

    assert insight is None

def test_deve_identificar_empate_no_tempo_medio_de_finalizacao():
    import pandas as pd

    analytics = NegociacaoAnalytics()

    analise_tempo_finalizacao = pd.DataFrame([
        {
            "tipoNegociacao": "TROCA",
            "tempoMedioDias": 3.0,
            "totalFinalizadas": 5
        },
        {
            "tipoNegociacao": "VENDA",
            "tempoMedioDias": 3.0,
            "totalFinalizadas": 8
        }
    ])

    insight = analytics._gerar_insight_tempo_finalizacao(
        analise_tempo_finalizacao
    )

    assert insight is not None
    assert insight["dados"]["modalidadeMaisRapida"] == "EMPATE"

def test_deve_identificar_estabilidade_na_evolucao_temporal():
    import pandas as pd

    analytics = NegociacaoAnalytics()

    negociacoes_por_mes = pd.DataFrame([
        {
            "mesNegociacao": "2026-01",
            "quantidade": 10
        },
        {
            "mesNegociacao": "2026-02",
            "quantidade": 10
        }
    ])

    insight = analytics._gerar_insight_evolucao_temporal(
        negociacoes_por_mes
    )

    assert insight is not None

def test_deve_tratar_mes_anterior_com_zero_negociacoes():
    import pandas as pd

    analytics = NegociacaoAnalytics()

    negociacoes_por_mes = pd.DataFrame([
        {
            "mesNegociacao": "2026-01",
            "quantidade": 0
        },
        {
            "mesNegociacao": "2026-02",
            "quantidade": 10
        }
    ])

    insight = analytics._gerar_insight_evolucao_temporal(
        negociacoes_por_mes
    )

    assert insight is not None

def test_deve_retornar_none_quando_houver_menos_de_dois_meses():
    import pandas as pd

    analytics = NegociacaoAnalytics()

    negociacoes_por_mes = pd.DataFrame([
        {
            "mesNegociacao": "2026-01",
            "quantidade": 10
        }
    ])

    insight = analytics._gerar_insight_evolucao_temporal(
        negociacoes_por_mes
    )

    assert insight is None


def test_deve_retornar_none_quando_houver_apenas_um_nivel_de_afinidade():
    import pandas as pd

    analytics = NegociacaoAnalytics()

    analise_afinidade = pd.DataFrame([
        {
            "afinidade": "ALTA",
            "taxaFinalizacao": 0.8,
            "totalNegociacoes": 10,
            "totalFinalizadas": 8
        }
    ])

    insight = analytics._gerar_insight_afinidade(
        analise_afinidade
    )

    assert insight is None