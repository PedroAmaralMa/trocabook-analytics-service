"""
Serviço orquestrador de analytics da plataforma Trocabook.

Responsável por receber os dados brutos de domínio (anúncios, negociações e utilizadores),
encaminhar aos respetivos analisadores e consolidar o painel executivo.
"""

import logging
from typing import Any, Sequence

import pandas as pd

from app.analytics.anuncio_analytics import AnuncioAnalytics
from app.analytics.negociacao_analytics import NegociacaoAnalytics
from app.analytics.previsao_temporal_analytics import PrevisaoTemporalAnalytics
from app.models.anuncio import Anuncio
from app.models.negociacao import Negociacao
from app.models.usuario import Usuario

logger = logging.getLogger(__name__)


class TrocabookAnalyticsService:
    """Coordenador central de análises descritivas, diagnósticas e preditivas."""

    def __init__(
        self,
        anuncio_analytics: AnuncioAnalytics | None = None,
        negociacao_analytics: NegociacaoAnalytics | None = None,
        previsao_analytics: PrevisaoTemporalAnalytics | None = None,
    ) -> None:
        """Inicializa o serviço com as instâncias dos analisadores.

        Args:
            anuncio_analytics: Instância responsável pela análise de anúncios.
            negociacao_analytics: Instância responsável pela análise de negociações.
            previsao_analytics: Instância responsável pelas previsões temporais.
        """
        self.anuncio_analytics = anuncio_analytics or AnuncioAnalytics()
        self.negociacao_analytics = negociacao_analytics or NegociacaoAnalytics()
        self.previsao_analytics = previsao_analytics or PrevisaoTemporalAnalytics()

    def gerar_relatorio_consolidado(
        self,
        anuncios: Sequence[Anuncio | dict[str, Any]],
        negociacoes: list[Negociacao],
        usuarios: list[Usuario] | None = None,
        horizonte_previsao: int = 12,
        quantidade_teste: int = 6,
    ) -> dict[str, Any]:
        """Executa todas as análises e previsões da plataforma.

        Args:
            anuncios: Lista de anúncios ativos/históricos.
            negociacoes: Lista de negociações.
            usuarios: Lista de utilizadores para previsão de novos registos.
            horizonte_previsao: Meses futuros para projeção temporal.
            quantidade_teste: Meses reservados para validação do modelo.

        Returns:
            Dicionário unificado contendo análises de anúncios, negociações,
            previsões de tendência e lista consolidada de insights.
        """
        logger.info(
            "Iniciando relatório consolidado. Anúncios: %d | Negociações: %d | Utilizadores: %d",
            len(anuncios) if anuncios else 0,
            len(negociacoes) if negociacoes else 0,
            len(usuarios) if usuarios else 0,
        )

        # 1. Análise Descritiva de Anúncios
        analise_anuncios = self.anuncio_analytics.analisar(anuncios)

        # 2. Análise Descritiva e Diagnóstica de Negociações
        analise_negociacoes = self.negociacao_analytics.analisar(negociacoes)

        # 3. Previsão Temporal de Anúncios
        previsao_anuncios = self._prever_anuncios(
            analise_anuncios=analise_anuncios,
            horizonte=horizonte_previsao,
            quantidade_teste=quantidade_teste,
        )

        # 4. Previsão Temporal de Utilizadores (se informados)
        previsao_usuarios = self._prever_usuarios(
            usuarios=usuarios or [],
            horizonte=horizonte_previsao,
            quantidade_teste=quantidade_teste,
        )

        # 5. Consolidação de Insights Globais
        insights_globais = self._consolidar_insights(
            analise_anuncios.get("insights", []),
            analise_negociacoes.get("insights", []),
        )

        return {
            "anuncios": analise_anuncios,
            "negociacoes": analise_negociacoes,
            "previsoes": {
                "anuncios": previsao_anuncios,
                "usuarios": previsao_usuarios,
            },
            "insights": insights_globais,
        }

    def _prever_anuncios(
        self,
        analise_anuncios: dict[str, Any],
        horizonte: int,
        quantidade_teste: int,
    ) -> dict[str, Any] | None:
        """Extrai a série de anúncios por mês e executa a regressão linear.

        Args:
            analise_anuncios: Dicionário retornado pela análise descritiva de anúncios.
            horizonte: Quantidade de meses futuros a serem projetados.
            quantidade_teste: Quantidade de meses reservados para avaliação do modelo.

        Returns:
            Dicionário com a previsão temporal de anúncios ou ``None`` se a série
            estiver vazia ou indisponível.
        """
        serie_anuncios = analise_anuncios.get("temporal", {}).get("anunciosPorMes")

        if serie_anuncios is None or serie_anuncios.empty:
            logger.warning("Série temporal de anúncios vazia. Previsão omitida.")
            return None

        return self.previsao_analytics.prever(
            serie_mensal=serie_anuncios,
            coluna_periodo="mesCriacao",
            coluna_valor="novosAnuncios",
            horizonte=horizonte,
            quantidade_teste=quantidade_teste,
        )

    def _prever_usuarios(
        self,
        usuarios: list[Usuario],
        horizonte: int,
        quantidade_teste: int,
    ) -> dict[str, Any] | None:
        """Monta o DataFrame mensal de novos utilizadores e executa a previsão.

        Args:
            usuarios: Lista de objetos de utilizadores contendo as datas de criação.
            horizonte: Quantidade de meses futuros a serem projetados.
            quantidade_teste: Quantidade de meses reservados para avaliação do modelo.

        Returns:
            Dicionário com a previsão temporal de utilizadores ou ``None`` se a
            lista estiver vazia ou o histórico for insuficiente.
        """
        if not usuarios:
            return None

        df_usuarios = pd.DataFrame([{"dataCriacao": u.dataCriacao} for u in usuarios])
        df_usuarios["mesCriacao"] = pd.to_datetime(
            df_usuarios["dataCriacao"], errors="coerce"
        ).dt.to_period("M")

        serie_usuarios = (
            df_usuarios.dropna(subset=["mesCriacao"])
            .groupby("mesCriacao")
            .size()
            .reset_index(name="quantidade")
        )

        if len(serie_usuarios) < (quantidade_teste + 2):
            logger.warning("Histórico de utilizadores insuficiente para previsão.")
            return None

        return self.previsao_analytics.prever(
            serie_mensal=serie_usuarios,
            coluna_periodo="mesCriacao",
            coluna_valor="quantidade",
            horizonte=horizonte,
            quantidade_teste=quantidade_teste,
        )

    @staticmethod
    def _consolidar_insights(
        insights_anuncios: list[str],
        insights_negociacoes: list[dict[str, Any] | str],
    ) -> list[dict[str, Any]]:
        """Unifica e padroniza os insights gerados pelos módulos.

        Args:
            insights_anuncios: Lista de mensagens textuais geradas pelo AnuncioAnalytics.
            insights_negociacoes: Lista de insights estruturados gerados pelo NegociacaoAnalytics.

        Returns:
            Lista de dicionários padronizados com os campos ``origem`` e ``conteudo``.
        """
        insights = []
        for item in insights_anuncios:
            insights.append({"origem": "ANUNCIOS", "conteudo": item})

        for item in insights_negociacoes:
            insights.append({"origem": "NEGOCIACOES", "conteudo": item})

        return insights