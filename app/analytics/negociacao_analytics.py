"""
Módulo responsável pelo processamento e análise dos dados de negociações do Trocabook.
"""

import logging

import pandas as pd

import numpy as np

from scipy.optimize import minimize
from scipy.special import betaln

from app.models.negociacao import Negociacao


logger = logging.getLogger(__name__)


class NegociacaoAnalytics:
    """
    Responsável pelo processamento e análise dos dados de negociações do Trocabook.
    """

    def analisar(
            self,
            negociacoes: list[Negociacao]
    ) -> dict:
        """
        Executa as análises dos dados de negociações do Trocabook.

        Coordena o processamento dos dados, o cálculo dos indicadores
        históricos, as análises de confiabilidade e a geração de insights
        automáticos.

        Args:
            negociacoes: Lista de negociações a serem analisadas.

        Returns:
            Dicionário contendo os resultados consolidados das análises
            de negociações.
        """
        logger.info(
            "Iniciando análise de negociações. Registros recebidos: %d.",
            len(negociacoes)
        )

        dataframe = self._converter_negociacoes_dataframe(negociacoes)

        if dataframe.empty:
            logger.info(
                "Análise de negociações concluída sem dados disponíveis."
            )

            return {
                "geral": {
                    "totalNegociacoes": 0,
                    "negociacoesPorStatus": pd.DataFrame(
                        columns=["status", "quantidade"]
                    ),
                    "negociacoesPorTipo": pd.DataFrame(
                        columns=["tipoNegociacao", "quantidade"]
                    )
                },
                "porTipo": pd.DataFrame(
                    columns=[
                        "tipoNegociacao",
                        "totalNegociacoes",
                        "totalFinalizadas",
                        "taxaFinalizacao"
                    ]
                ),
                "porCategoria": pd.DataFrame(
                    columns=[
                        "categoria",
                        "totalNegociacoes",
                        "totalFinalizadas",
                        "taxaFinalizacao",
                        "taxaFinalizacaoAjustada"
                    ]
                ),
                "afinidadeCategorias": pd.DataFrame(
                    columns=[
                        "afinidade",
                        "totalNegociacoes",
                        "totalFinalizadas",
                        "taxaFinalizacao"
                    ]
                ),
                "combinacoesCategorias": pd.DataFrame(
                    columns=[
                        "categoriaAnuncio",
                        "categoriaAnuncioOferecido",
                        "totalNegociacoes",
                        "totalFinalizadas",
                        "taxaFinalizacao",
                        "taxaFinalizacaoAjustada"
                    ]
                ),
                "temporal": {
                    "negociacoesPorMes": pd.DataFrame(
                        columns=["mesNegociacao", "quantidade"]
                    ),
                    "negociacoesPorMesTipo": pd.DataFrame(
                        columns=[
                            "mesNegociacao",
                            "tipoNegociacao",
                            "quantidade"
                        ]
                    ),
                    "finalizacoesPorMes": pd.DataFrame(
                        columns=["mesFinalizacao", "quantidade"]
                    ),
                    "tempoFinalizacao": pd.DataFrame(
                        columns=[
                            "tipoNegociacao",
                            "totalFinalizadas",
                            "tempoMedioDias"
                        ]
                    ),
                    "taxaFinalizacaoPorMesInicio": pd.DataFrame(
                        columns=[
                            "mesNegociacao",
                            "totalNegociacoes",
                            "totalFinalizadas",
                            "taxaFinalizacao"
                        ]
                    )
                },
                "insights": []
            }

        analise_geral = self._analisar_geral(dataframe)

        analise_por_tipo = self._analisar_por_tipo(dataframe)

        analise_por_categoria = self._analisar_por_categoria(dataframe)

        analise_afinidade = self._analisar_afinidade_categorias(dataframe)

        analise_combinacoes = self._analisar_combinacoes_categorias(dataframe)

        analise_categorias_ajustada = (
            self._analisar_confiabilidade_categorias(
                analise_por_categoria
            )
        )

        analise_combinacoes_ajustada = (
            self._analisar_confiabilidade_combinacoes_categorias(
                analise_combinacoes
            )
        )

        analise_temporal = self._analisar_negociacoes_por_mes(
            dataframe
        )

        finalizacoes_por_mes = self._analisar_finalizacoes_por_mes(
            dataframe
        )

        tempo_finalizacao = self._analisar_tempo_finalizacao(
            dataframe
        )

        taxa_finalizacao_por_mes_inicio = (
            self._analisar_taxa_finalizacao_por_mes_inicio(
                dataframe
            )
        )

        insight_tipo = self._gerar_insight_tipo_negociacao(
            analise_por_tipo
        )

        insight_categoria = self._gerar_insight_categoria(
            analise_categorias_ajustada
        )

        insight_tempo_finalizacao = self._gerar_insight_tempo_finalizacao(
            tempo_finalizacao
        )

        insight_evolucao_temporal = self._gerar_insight_evolucao_temporal(
            analise_temporal["negociacoesPorMes"]
        )

        insight_afinidade = self._gerar_insight_afinidade(
            analise_afinidade
        )

        insight_combinacoes = self._gerar_insight_combinacoes_categorias(
            analise_combinacoes_ajustada
        )

        insights = [
            insight
            for insight in [
                insight_tipo,
                insight_categoria,
                insight_tempo_finalizacao,
                insight_evolucao_temporal,
                insight_afinidade,
                insight_combinacoes
            ]
            if insight is not None
        ]

        resultado = {
            "geral": analise_geral,
            "porTipo": analise_por_tipo,
            "porCategoria": analise_categorias_ajustada,
            "afinidadeCategorias": analise_afinidade,
            "combinacoesCategorias": analise_combinacoes_ajustada,
            "temporal": {
                "negociacoesPorMes": analise_temporal["negociacoesPorMes"],
                "negociacoesPorMesTipo": analise_temporal["negociacoesPorMesTipo"],
                "finalizacoesPorMes": finalizacoes_por_mes,
                "tempoFinalizacao": tempo_finalizacao,
                "taxaFinalizacaoPorMesInicio": taxa_finalizacao_por_mes_inicio
            },
            "insights": insights
        }

        logger.info(
            "Análise de negociações concluída. "
            "Registros analisados: %d. Insights gerados: %d.",
            len(dataframe),
            len(insights)
        )

        return resultado


    def _converter_negociacoes_dataframe(
        self,
        negociacoes: list[Negociacao]
    ) -> pd.DataFrame:
        """
        Converte a lista de negociações em um DataFrame do Pandas para processamento dos dados.

        Args:
            negociacoes: Lista de objetos Negociacao a serem convertidos.

        Returns:
            DataFrame contendo os dados estruturados das negociações.
        """
        logger.debug(
            "Convertendo %d negociações para DataFrame.",
            len(negociacoes)
        )

        dados = []

        for negociacao in negociacoes:
            dados.append({
                "id": negociacao.id,
                "anuncioId": negociacao.anuncioId,
                "anuncioOferecidoId": negociacao.anuncioOferecidoId,
                "categoriasAnuncio": negociacao.categoriasAnuncio,
                "categoriasAnuncioOferecido": negociacao.categoriasAnuncioOferecido,
                "dataNegociacao": negociacao.dataNegociacao,
                "dataFinalizacao": negociacao.dataFinalizacao,
                "tipoNegociacao": negociacao.tipoNegociacao.value,
                "status": negociacao.status.value
            })

        dataframe = pd.DataFrame(
            dados,
            columns=[
                "id",
                "anuncioId",
                "anuncioOferecidoId",
                "categoriasAnuncio",
                "categoriasAnuncioOferecido",
                "dataNegociacao",
                "dataFinalizacao",
                "tipoNegociacao",
                "status"
            ]
        )

        logger.debug(
            "Conversão de negociações concluída. "
            "Registros no DataFrame: %d.",
            len(dataframe)
        )

        return dataframe


    def _analisar_geral(
        self,
        dataframe: pd.DataFrame
    ) -> dict:
        """
        Calcula os indicadores gerais das negociações.

        A análise considera a quantidade total de negociações e suas
        distribuições por status e por tipo de negociação.

        Args:
            dataframe: DataFrame contendo os dados das negociações.

        Returns:
            Dicionário contendo a quantidade total de negociações,
            a distribuição por status e a distribuição por tipo.
        """
        logger.debug("Iniciando análise geral das negociações.")

        total_negociacoes = len(dataframe)

        negociacoes_por_status = (
            dataframe["status"]
            .value_counts()
            .reset_index()
        )

        negociacoes_por_status.columns = [
            "status",
            "quantidade"
        ]

        negociacoes_por_tipo = (
            dataframe["tipoNegociacao"]
            .value_counts()
            .reset_index()
        )

        negociacoes_por_tipo.columns = [
            "tipoNegociacao",
            "quantidade"
        ]

        logger.debug(
            "Análise geral concluída. Total de negociações: %d.",
            total_negociacoes
        )

        return {
            "totalNegociacoes": total_negociacoes,
            "negociacoesPorStatus": negociacoes_por_status,
            "negociacoesPorTipo": negociacoes_por_tipo
        }

    def _analisar_por_tipo(
        self,
        dataframe: pd.DataFrame
    ) -> pd.DataFrame:
        """
        Calcula os indicadores de conclusão das negociações agrupados por tipo.

        A análise considera as modalidades TROCA e VENDA, calculando a
        quantidade total de negociações, a quantidade de negociações
        finalizadas e a respectiva taxa de finalização.

        Args:
            dataframe: DataFrame contendo os dados das negociações.

        Returns:
            DataFrame contendo os indicadores de conclusão agrupados
            por tipo de negociação.
        """
        logger.debug("Iniciando análise das negociações por tipo.")

        negociacoes_validas = dataframe[
            dataframe["tipoNegociacao"].isin(["TROCA", "VENDA"])
        ].copy()

        negociacoes_validas["finalizada"] = (
            negociacoes_validas["status"] == "FINALIZADA"
        )

        analise_por_tipo = (
            negociacoes_validas
            .groupby("tipoNegociacao")
            .agg(
                totalNegociacoes=("id", "count"),
                totalFinalizadas=("finalizada", "sum")
            )
            .reset_index()
        )

        analise_por_tipo["taxaFinalizacao"] = (
            analise_por_tipo["totalFinalizadas"]
            / analise_por_tipo["totalNegociacoes"]
        )

        logger.debug(
            "Análise por tipo concluída. Tipos analisados: %d.",
            len(analise_por_tipo)
        )

        return analise_por_tipo

    def _analisar_por_categoria(
        self,
        dataframe: pd.DataFrame
    ) -> pd.DataFrame:
        """
        Calcula os indicadores de conclusão das negociações agrupados
        pelas categorias dos anúncios negociados.

        Anúncios que possuem múltiplas categorias são expandidos para
        permitir que cada categoria participe individualmente da análise.

        Args:
            dataframe: DataFrame contendo os dados das negociações.

        Returns:
            DataFrame contendo a quantidade total de negociações,
            a quantidade de negociações finalizadas e a taxa de
            finalização de cada categoria.
        """
        logger.debug("Iniciando análise das negociações por categoria.")

        negociacoes_por_categoria = dataframe[
            [
                "id",
                "categoriasAnuncio",
                "status"
            ]
        ].copy()

        negociacoes_por_categoria = (
            negociacoes_por_categoria
            .explode("categoriasAnuncio")
            .rename(
                columns={
                    "categoriasAnuncio": "categoria"
                }
            )
        )

        negociacoes_por_categoria = (
            negociacoes_por_categoria
            .drop_duplicates(subset=["id", "categoria"])
        )

        negociacoes_por_categoria["finalizada"] = (
            negociacoes_por_categoria["status"] == "FINALIZADA"
        )

        analise_por_categoria = (
            negociacoes_por_categoria
            .groupby("categoria")
            .agg(
                totalNegociacoes=("id", "count"),
                totalFinalizadas=("finalizada", "sum")
            )
            .reset_index()
        )

        analise_por_categoria["taxaFinalizacao"] = (
            analise_por_categoria["totalFinalizadas"]
            / analise_por_categoria["totalNegociacoes"]
        )

        analise_por_categoria = (
            analise_por_categoria
            .sort_values(
                by="taxaFinalizacao",
                ascending=False
            )
            .reset_index(drop=True)
        )

        logger.debug(
            "Análise por categoria concluída. Categorias analisadas: %d.",
            len(analise_por_categoria)
        )

        return analise_por_categoria

    def _classificar_afinidade(
        self,
        categorias_anuncio: list[str],
        categorias_anuncio_oferecido: list[str]
    ) -> str:
        """
        Classifica a afinidade entre as categorias dos dois livros
        envolvidos em uma negociação de troca.

        Args:
            categorias_anuncio: Categorias do anúncio principal.
            categorias_anuncio_oferecido: Categorias do anúncio oferecido.

        Returns:
            Classificação da afinidade como MESMA, SEMELHANTE ou DIFERENTE.
        """
        categorias_principal = set(categorias_anuncio)
        categorias_oferecido = set(categorias_anuncio_oferecido)

        if categorias_principal == categorias_oferecido:
            return "MESMA"

        if categorias_principal & categorias_oferecido:
            return "SEMELHANTE"

        return "DIFERENTE"

    def _analisar_afinidade_categorias(
        self,
        dataframe: pd.DataFrame
    ) -> pd.DataFrame:
        """
        Analisa a relação entre a afinidade das categorias dos livros
        envolvidos em trocas e a finalização das negociações.

        São consideradas apenas negociações do tipo TROCA que possuem
        anúncio oferecido e categorias disponíveis para ambos os livros.

        Args:
            dataframe: DataFrame contendo os dados das negociações.

        Returns:
            DataFrame contendo a quantidade total de trocas,
            a quantidade de trocas finalizadas e a taxa de finalização
            para cada nível de afinidade.
        """
        logger.debug(
            "Iniciando análise de afinidade entre categorias nas trocas."
        )

        trocas = dataframe[
            (dataframe["tipoNegociacao"] == "TROCA")
            & dataframe["anuncioOferecidoId"].notna()
            & dataframe["categoriasAnuncio"].notna()
            & dataframe["categoriasAnuncioOferecido"].notna()
        ].copy()

        if trocas.empty:
            logger.info(
                "Análise de afinidade sem dados: "
                "nenhuma troca válida encontrada."
            )

            return pd.DataFrame(
                columns=[
                    "afinidade",
                    "totalNegociacoes",
                    "totalFinalizadas",
                    "taxaFinalizacao"
                ]
            )

        trocas["afinidade"] = trocas.apply(
            lambda linha: self._classificar_afinidade(
                linha["categoriasAnuncio"],
                linha["categoriasAnuncioOferecido"]
            ),
            axis=1
        )

        trocas["finalizada"] = (
            trocas["status"] == "FINALIZADA"
        )

        analise_afinidade = (
            trocas
            .groupby("afinidade")
            .agg(
                totalNegociacoes=("id", "count"),
                totalFinalizadas=("finalizada", "sum")
            )
            .reset_index()
        )

        analise_afinidade["taxaFinalizacao"] = (
            analise_afinidade["totalFinalizadas"]
            / analise_afinidade["totalNegociacoes"]
        )

        logger.debug(
            "Análise de afinidade concluída. "
            "Níveis de afinidade analisados: %d.",
            len(analise_afinidade)
        )

        return analise_afinidade

    def _analisar_combinacoes_categorias(
        self,
        dataframe: pd.DataFrame
    ) -> pd.DataFrame:
        """
        Analisa as combinações entre as categorias dos livros envolvidos
        nas negociações de troca.

        Cada combinação entre uma categoria do anúncio principal e uma
        categoria do anúncio oferecido é considerada individualmente,
        permitindo identificar quais pares aparecem com maior frequência
        e suas respectivas taxas de finalização.

        Args:
            dataframe: DataFrame contendo os dados das negociações.

        Returns:
            DataFrame contendo as combinações de categorias, a quantidade
            total de negociações, a quantidade de negociações finalizadas
            e a taxa de finalização de cada combinação.
        """
        logger.debug(
            "Iniciando análise das combinações de categorias nas trocas."
        )

        trocas = dataframe[
            (dataframe["tipoNegociacao"] == "TROCA")
            & dataframe["anuncioOferecidoId"].notna()
            & dataframe["categoriasAnuncio"].notna()
            & dataframe["categoriasAnuncioOferecido"].notna()
        ].copy()

        combinacoes = (
            trocas
            .explode("categoriasAnuncio")
            .explode("categoriasAnuncioOferecido")
            .rename(
                columns={
                    "categoriasAnuncio": "categoriaAnuncio",
                    "categoriasAnuncioOferecido": "categoriaAnuncioOferecido"
                }
            )
        )

        combinacoes["finalizada"] = (
            combinacoes["status"] == "FINALIZADA"
        )

        analise_combinacoes = (
            combinacoes
            .groupby(
                [
                    "categoriaAnuncio",
                    "categoriaAnuncioOferecido"
                ]
            )
            .agg(
                totalNegociacoes=("id", "count"),
                totalFinalizadas=("finalizada", "sum")
            )
            .reset_index()
        )

        analise_combinacoes["taxaFinalizacao"] = (
            analise_combinacoes["totalFinalizadas"]
            / analise_combinacoes["totalNegociacoes"]
        )

        analise_combinacoes = (
            analise_combinacoes
            .sort_values(
                by="totalNegociacoes",
                ascending=False
            )
            .reset_index(drop=True)
        )

        logger.debug(
            "Análise das combinações de categorias concluída. "
            "Combinações analisadas: %d.",
            len(analise_combinacoes)
        )

        return analise_combinacoes

    def _analisar_negociacoes_por_mes(
        self,
        dataframe: pd.DataFrame
    ) -> dict:
        """
        Analisa a evolução mensal das negociações iniciadas.

        As negociações são agrupadas pelo mês de início, permitindo
        observar o volume total registrado em cada período e sua
        distribuição entre os tipos de negociação.

        Args:
            dataframe: DataFrame contendo os dados das negociações.

        Returns:
            Dicionário contendo a quantidade de negociações iniciadas
            por mês e a distribuição mensal por tipo de negociação.
        """
        logger.debug(
            "Iniciando análise mensal das negociações."
        )

        negociacoes_temporais = dataframe.copy()

        negociacoes_temporais["mesNegociacao"] = (
            negociacoes_temporais["dataNegociacao"]
            .dt.to_period("M")
            .astype(str)
        )

        negociacoes_por_mes = (
            negociacoes_temporais
            .groupby("mesNegociacao")
            .size()
            .reset_index(name="quantidade")
        )

        negociacoes_por_mes_tipo = (
            negociacoes_temporais[
                negociacoes_temporais["tipoNegociacao"].isin(
                    ["TROCA", "VENDA"]
                )
            ]
            .groupby(
                [
                    "mesNegociacao",
                    "tipoNegociacao"
                ]
            )
            .size()
            .reset_index(name="quantidade")
        )

        logger.debug(
            "Análise mensal concluída. Períodos analisados: %d.",
            len(negociacoes_por_mes)
        )

        return {
            "negociacoesPorMes": negociacoes_por_mes,
            "negociacoesPorMesTipo": negociacoes_por_mes_tipo
        }

    def _analisar_finalizacoes_por_mes(
            self,
            dataframe: pd.DataFrame
    ) -> pd.DataFrame:
        """
        Analisa a quantidade de negociações finalizadas em cada mês.

        São consideradas apenas negociações com status FINALIZADA,
        utilizando a data de finalização para identificar o período
        em que a conclusão ocorreu.

        Args:
            dataframe: DataFrame contendo os dados das negociações.

        Returns:
            DataFrame contendo a quantidade de negociações finalizadas
            em cada mês.
        """
        logger.debug(
            "Iniciando análise mensal das negociações finalizadas."
        )



        negociacoes_finalizadas = dataframe[
            (dataframe["status"] == "FINALIZADA")
            & dataframe["dataFinalizacao"].notna()
            ].copy()

        if negociacoes_finalizadas.empty:
            logger.warning(
                "Análise mensal de finalizações sem dados: "
                "nenhuma negociação foi finalizada."
            )

            return pd.DataFrame(
                columns=["mesFinalizacao", "quantidade"]
            )

        negociacoes_finalizadas["mesFinalizacao"] = (
            negociacoes_finalizadas["dataFinalizacao"]
            .dt.to_period("M")
            .astype(str)
        )

        finalizacoes_por_mes = (
            negociacoes_finalizadas
            .groupby("mesFinalizacao")
            .size()
            .reset_index(name="quantidade")
        )

        logger.debug(
            "Análise mensal de finalizações concluída. "
            "Períodos analisados: %d.",
            len(finalizacoes_por_mes)
        )

        return finalizacoes_por_mes

    def _analisar_tempo_finalizacao(
            self,
            dataframe: pd.DataFrame
    ) -> pd.DataFrame:
        """
        Analisa o tempo necessário para a conclusão das negociações
        agrupado por tipo.

        São consideradas apenas negociações finalizadas que possuem
        as datas de início e finalização disponíveis. A duração de cada
        negociação é calculada em dias e utilizada para obter o tempo
        médio de finalização de cada tipo de negociação.

        Args:
            dataframe: DataFrame contendo os dados das negociações.

        Returns:
            DataFrame contendo a quantidade de negociações finalizadas
            e o tempo médio de finalização em dias para cada tipo.
        """
        logger.debug(
            "Iniciando análise do tempo de finalização das negociações."
        )

        negociacoes_finalizadas = dataframe[
            (dataframe["status"] == "FINALIZADA")
            & dataframe["dataFinalizacao"].notna()
            & dataframe["dataNegociacao"].notna()
            & dataframe["tipoNegociacao"].isin(["TROCA", "VENDA"])
            ].copy()

        if negociacoes_finalizadas.empty:
            logger.warning(
                "Análise do tempo de finalização sem dados: "
                "nenhuma negociação foi finalizada."
            )

            return pd.DataFrame(
                columns=[
                    "tipoNegociacao",
                    "totalFinalizadas",
                    "tempoMedioDias"
                ]
            )

        negociacoes_finalizadas = negociacoes_finalizadas[
            negociacoes_finalizadas["dataFinalizacao"]
            >= negociacoes_finalizadas["dataNegociacao"]
        ].copy()


        negociacoes_finalizadas["tempoFinalizacao"] = (
            negociacoes_finalizadas["dataFinalizacao"]
            - negociacoes_finalizadas["dataNegociacao"]
        )

        negociacoes_finalizadas["diasAteFinalizacao"] = (
            negociacoes_finalizadas["tempoFinalizacao"]
            .dt.total_seconds()
            / 86400
        )

        tempo_medio_por_tipo = (
            negociacoes_finalizadas
            .groupby("tipoNegociacao")
            .agg(
                totalFinalizadas=("id", "count"),
                tempoMedioDias=("diasAteFinalizacao", "mean")
            )
            .reset_index()
        )

        logger.debug(
            "Análise do tempo de finalização concluída. "
            "Tipos analisados: %d.",
            len(tempo_medio_por_tipo)
        )

        return tempo_medio_por_tipo

    def _analisar_taxa_finalizacao_por_mes_inicio(
            self,
            dataframe: pd.DataFrame
    ) -> pd.DataFrame:
        """
        Analisa a taxa de finalização das negociações agrupadas pelo
        mês em que foram iniciadas.

        Cada negociação permanece associada ao seu mês de início,
        independentemente do período em que sua finalização ocorreu.

        Args:
            dataframe: DataFrame contendo os dados das negociações.

        Returns:
            DataFrame contendo a quantidade total de negociações,
            a quantidade de negociações finalizadas e a taxa de
            finalização para cada mês de início.
        """
        logger.debug(
            "Iniciando análise da taxa de finalização por mês de início."
        )

        negociacoes_temporais = dataframe.copy()

        negociacoes_temporais["mesNegociacao"] = (
            negociacoes_temporais["dataNegociacao"]
            .dt.to_period("M")
            .astype(str)
        )

        negociacoes_temporais["finalizada"] = (
            negociacoes_temporais["status"] == "FINALIZADA"
        )

        indicadores_temporais = (
            negociacoes_temporais
            .groupby("mesNegociacao")
            .agg(
                totalNegociacoes=("id", "count"),
                totalFinalizadas=("finalizada", "sum")
            )
            .reset_index()
        )

        indicadores_temporais["taxaFinalizacao"] = (
            indicadores_temporais["totalFinalizadas"]
            / indicadores_temporais["totalNegociacoes"]
        )

        logger.debug(
            "Análise da taxa de finalização por mês de início concluída. "
            "Períodos analisados: %d.",
            len(indicadores_temporais)
        )

        return indicadores_temporais

    def _calcular_log_verossimilhanca_negativa(
            self,
            parametros: np.ndarray,
            finalizacoes: np.ndarray,
            nao_finalizacoes: np.ndarray
    ) -> float:
        """
        Calcula a log-verossimilhança negativa dos parâmetros
        da distribuição Beta-Binomial.

        O valor negativo é utilizado porque o otimizador busca
        minimizar a função, enquanto a estimação por máxima
        verossimilhança procura maximizar a verossimilhança dos dados.

        Args:
            parametros: Vetor contendo as forças de finalização e
                não finalização.
            finalizacoes: Quantidades de negociações finalizadas
                observadas em cada grupo.
            nao_finalizacoes: Quantidades de negociações não finalizadas
                observadas em cada grupo.

        Returns:
            Valor da log-verossimilhança negativa dos parâmetros.
        """
        forca_finalizacao = parametros[0]
        forca_nao_finalizacao = parametros[1]

        log_verossimilhancas = (
            betaln(
                finalizacoes + forca_finalizacao,
                nao_finalizacoes + forca_nao_finalizacao
            )
            - betaln(
                forca_finalizacao,
                forca_nao_finalizacao
            )
        )

        return float(-log_verossimilhancas.sum())

    def _estimar_parametros_beta_binomial(
            self,
            indicadores: pd.DataFrame
    ) -> tuple[float, float]:
        """
        Estima os parâmetros da distribuição Beta-Binomial a partir
        dos resultados históricos observados entre diferentes grupos.

        A estimação utiliza máxima verossimilhança considerando as
        quantidades de negociações finalizadas e não finalizadas de
        cada grupo.

        Args:
            indicadores: DataFrame contendo os indicadores históricos
                dos grupos analisados.

        Returns:
            Tupla contendo a força de finalização e a força de
            não finalização estimadas.

        Raises:
            ValueError: Se não houver grupos suficientes para realizar
                a estimação ou se a otimização não convergir.
        """
        logger.debug(
            "Iniciando estimação dos parâmetros Beta-Binomial."
        )

        if len(indicadores) < 2:
            raise ValueError(
                 "São necessários pelo menos dois grupos "
                 "para estimar os parâmetros Beta-Binomial."
            )

        finalizacoes = (
            indicadores["totalFinalizadas"]
            .to_numpy(dtype=float)
        )

        negociacoes = (
            indicadores["totalNegociacoes"]
            .to_numpy(dtype=float)
        )

        nao_finalizacoes = negociacoes - finalizacoes

        resultado = minimize(
            self._calcular_log_verossimilhanca_negativa,
            x0=np.array([1.0, 1.0]),
            args=(
                finalizacoes,
                nao_finalizacoes
            ),
            bounds=[
                (0.0001, None),
                (0.0001, None)
            ],
            method="L-BFGS-B"
        )

        if not resultado.success:
            raise ValueError(
                "Não foi possível estimar os parâmetros Beta-Binomial."
            )

        forca_finalizacao = float(resultado.x[0])
        forca_nao_finalizacao = float(resultado.x[1])

        logger.debug(
            "Parâmetros Beta-Binomial estimados. "
            "Força de finalização: %.4f. "
            "Força de não finalização: %.4f.",
            forca_finalizacao,
            forca_nao_finalizacao
        )

        return forca_finalizacao, forca_nao_finalizacao

    def _aplicar_ajuste_beta_binomial(
            self,
            indicadores: pd.DataFrame,
            forca_finalizacao: float,
            forca_nao_finalizacao: float
    ) -> pd.DataFrame:
        """
        Aplica a suavização Beta-Binomial às taxas históricas de
        finalização dos grupos analisados.

        O ajuste combina os resultados observados de cada grupo
        com os parâmetros estimados da distribuição histórica,
        reduzindo a influência de taxas extremas provenientes de
        pequenas amostras.

        Args:
            indicadores: DataFrame contendo os indicadores históricos
                dos grupos analisados.
            forca_finalizacao: Força histórica associada às finalizações.
            forca_nao_finalizacao: Força histórica associada às
                não finalizações.

        Returns:
            DataFrame contendo os indicadores dos grupos e suas
            respectivas taxas de finalização ajustadas.
        """
        logger.debug(
            "Iniciando ajuste Beta-Binomial das taxas dos grupos."
        )

        indicadores_ajustados = indicadores.copy()

        forca_referencia = (
            forca_finalizacao
            + forca_nao_finalizacao
        )

        indicadores_ajustados["taxaFinalizacaoAjustada"] = (
            (
                indicadores_ajustados["totalFinalizadas"]
                + forca_finalizacao
            )
            /
            (
                indicadores_ajustados["totalNegociacoes"]
                + forca_referencia
            )
        )

        indicadores_ajustados = (
            indicadores_ajustados
            .sort_values(
                by="taxaFinalizacaoAjustada",
                ascending=False
            )
            .reset_index(drop=True)
        )

        logger.debug(
            "Ajuste Beta-Binomial concluído. Grupos ajustados: %d.",
            len(indicadores_ajustados)
        )

        return indicadores_ajustados

    def _analisar_confiabilidade_categorias(
            self,
            indicadores_categorias: pd.DataFrame
    ) -> pd.DataFrame:
        """
        Analisa a confiabilidade das taxas históricas de finalização
        das categorias utilizando suavização Beta-Binomial.

        Quando não houver grupos suficientes para estimar os parâmetros
        da distribuição, a análise continua utilizando a taxa histórica
        de finalização sem ajuste.

        Args:
            indicadores_categorias: DataFrame contendo os indicadores
                históricos calculados por categoria.

        Returns:
            DataFrame contendo os indicadores das categorias e suas
            taxas de finalização ajustadas quando possível.
        """
        logger.debug(
            "Iniciando análise de confiabilidade das categorias."
        )

        if len(indicadores_categorias) < 2:
            logger.warning(
                "Ajuste Beta-Binomial das categorias não realizado: "
                "são necessários pelo menos dois grupos."
            )

            indicadores_ajustados = indicadores_categorias.copy()

            indicadores_ajustados["taxaFinalizacaoAjustada"] = (
                indicadores_ajustados["taxaFinalizacao"]
            )

            return indicadores_ajustados

        forca_finalizacao, forca_nao_finalizacao = (
            self._estimar_parametros_beta_binomial(
                indicadores_categorias
            )
        )

        indicadores_ajustados = (
            self._aplicar_ajuste_beta_binomial(
                indicadores_categorias,
                forca_finalizacao,
                forca_nao_finalizacao
            )
        )

        logger.debug(
            "Análise de confiabilidade das categorias concluída."
        )

        return indicadores_ajustados

    def _analisar_confiabilidade_combinacoes_categorias(
            self,
            indicadores_combinacoes: pd.DataFrame
    ) -> pd.DataFrame:
        """
        Analisa a confiabilidade das taxas históricas de finalização
        das combinações de categorias utilizando suavização Beta-Binomial.

        Quando não houver grupos suficientes para estimar os parâmetros
        da distribuição, a análise continua utilizando a taxa histórica
        de finalização sem ajuste.

        Args:
            indicadores_combinacoes: DataFrame contendo os indicadores
                históricos calculados por combinação de categorias.

        Returns:
            DataFrame contendo os indicadores das combinações de categorias
            e suas taxas de finalização ajustadas quando possível.
        """
        logger.debug(
            "Iniciando análise de confiabilidade das combinações de categorias."
        )

        if len(indicadores_combinacoes) < 2:
            logger.warning(
                "Ajuste Beta-Binomial das combinações não realizado: "
                "são necessários pelo menos dois grupos."
            )

            indicadores_ajustados = indicadores_combinacoes.copy()

            indicadores_ajustados["taxaFinalizacaoAjustada"] = (
                indicadores_ajustados["taxaFinalizacao"]
            )

            return indicadores_ajustados

        forca_finalizacao, forca_nao_finalizacao = (
            self._estimar_parametros_beta_binomial(
                indicadores_combinacoes
            )
        )

        indicadores_ajustados = (
            self._aplicar_ajuste_beta_binomial(
                indicadores_combinacoes,
                forca_finalizacao,
                forca_nao_finalizacao
            )
        )

        logger.debug(
            "Análise de confiabilidade das combinações de categorias concluída."
        )

        return indicadores_ajustados

    def _gerar_insight_tipo_negociacao(
            self,
            analise_por_tipo: pd.DataFrame
    ) -> dict | None:
        """
        Gera um insight comparativo sobre o desempenho dos tipos
        de negociação.

        A comparação considera as taxas históricas de finalização
        de TROCA e VENDA, identificando qual modalidade apresentou
        maior taxa no período analisado.

        Args:
            analise_por_tipo: DataFrame contendo os indicadores de
                finalização agrupados por tipo de negociação.

        Returns:
            Dicionário contendo o insight gerado e os dados que
            sustentam a comparação, ou None quando não houver
            informações suficientes para comparar os dois tipos.
        """
        logger.debug(
            "Iniciando geração do insight por tipo de negociação."
        )

        tipos_disponiveis = set(
            analise_por_tipo["tipoNegociacao"]
        )

        if not {"TROCA", "VENDA"}.issubset(tipos_disponiveis):
            logger.debug(
                "Insight por tipo não gerado: TROCA e VENDA "
                "não estão simultaneamente disponíveis."
            )
            return None

        troca = analise_por_tipo[
            analise_por_tipo["tipoNegociacao"] == "TROCA"
        ].iloc[0]

        venda = analise_por_tipo[
            analise_por_tipo["tipoNegociacao"] == "VENDA"
        ].iloc[0]

        taxa_troca = float(troca["taxaFinalizacao"])
        taxa_venda = float(venda["taxaFinalizacao"])

        diferenca = taxa_troca - taxa_venda

        if np.isclose(taxa_troca, taxa_venda):
            modalidade_destaque = "EMPATE"
            mensagem = (
                "Trocas e vendas apresentaram a mesma taxa histórica "
                "de finalização no período analisado."
            )

        elif taxa_troca > taxa_venda:
            modalidade_destaque = "TROCA"
            mensagem = (
                "Trocas apresentaram maior taxa histórica de finalização "
                "do que vendas no período analisado."
            )

        else:
            modalidade_destaque = "VENDA"
            mensagem = (
                "Vendas apresentaram maior taxa histórica de finalização "
                "do que trocas no período analisado."
            )

        insight = {
            "tipo": "TIPO_NEGOCIACAO",
            "titulo": "Desempenho por tipo de negociação",
            "mensagem": mensagem,
            "dados": {
                "modalidadeDestaque": modalidade_destaque,
                "taxaFinalizacaoTroca": taxa_troca,
                "taxaFinalizacaoVenda": taxa_venda,
                "diferencaTaxaFinalizacao": abs(diferenca)
            }
        }

        logger.debug(
            "Insight por tipo de negociação gerado. "
            "Modalidade em destaque: %s.",
            modalidade_destaque
        )

        return insight

    def _gerar_insight_categoria(
            self,
            analise_categorias_ajustada: pd.DataFrame
    ) -> dict | None:
        """
        Gera um insight sobre a categoria com maior taxa histórica
        de finalização ajustada.

        A análise utiliza a taxa suavizada pelo modelo Beta-Binomial,
        reduzindo a influência de resultados extremos provenientes
        de categorias com poucas observações.

        Args:
            analise_categorias_ajustada: DataFrame contendo os indicadores
                históricos das categorias e suas taxas de finalização
                ajustadas.

        Returns:
            Dicionário contendo o insight da categoria em destaque
            e os dados que sustentam a interpretação, ou None quando
            não houver categorias disponíveis.
        """
        logger.debug(
            "Iniciando geração do insight por categoria."
        )

        if analise_categorias_ajustada.empty:
            logger.debug(
                "Insight por categoria não gerado: "
                "nenhuma categoria disponível."
            )
            return None

        maior_taxa_ajustada = float(
            analise_categorias_ajustada.iloc[0]["taxaFinalizacaoAjustada"]
        )

        categorias_destaque = analise_categorias_ajustada[
            np.isclose(
                analise_categorias_ajustada["taxaFinalizacaoAjustada"],
                maior_taxa_ajustada
            )
        ]

        if len(categorias_destaque) == 1:
            categoria_destaque = categorias_destaque.iloc[0]

            categoria = str(
                categoria_destaque["categoria"]
            )

            mensagem = (
                f"A categoria {categoria} apresentou a maior taxa histórica "
                "de finalização ajustada no período analisado."
            )

            categorias = [categoria]

        else:
            categorias = (
                categorias_destaque["categoria"]
                .astype(str)
                .tolist()
            )

            nomes_categorias = ", ".join(categorias)

            mensagem = (
                f"As categorias {nomes_categorias} apresentaram a mesma "
                "maior taxa histórica de finalização ajustada no período analisado."
            )

        dados_categorias = []

        for _, linha in categorias_destaque.iterrows():
            dados_categorias.append({
                "categoria": str(linha["categoria"]),
                "totalNegociacoes": int(linha["totalNegociacoes"]),
                "totalFinalizadas": int(linha["totalFinalizadas"]),
                "taxaFinalizacao": float(linha["taxaFinalizacao"]),
                "taxaFinalizacaoAjustada": float(
                    linha["taxaFinalizacaoAjustada"]
                )
            })


        insight = {
            "tipo": "CATEGORIA",
            "titulo": "Desempenho por categoria",
            "mensagem": mensagem,
            "dados": {
                "categoriasDestaque": dados_categorias
            }
        }

        logger.debug(
            "Insight por categoria gerado. "
            "Categorias em destaque: %s.",
            categorias
        )

        return insight

    def _gerar_insight_tempo_finalizacao(
            self,
            analise_tempo_finalizacao: pd.DataFrame
    ) -> dict | None:
        """
        Gera um insight comparativo sobre o tempo médio necessário
        para a finalização das negociações.

        A comparação considera o tempo médio histórico de finalização
        das modalidades TROCA e VENDA, identificando qual apresentou
        menor duração entre as negociações concluídas.

        Args:
            analise_tempo_finalizacao: DataFrame contendo a quantidade
                de negociações finalizadas e o tempo médio de
                finalização por tipo.

        Returns:
            Dicionário contendo o insight gerado e os dados que
            sustentam a comparação, ou None quando não houver
            informações suficientes para comparar os dois tipos.
        """
        logger.debug(
            "Iniciando geração do insight de tempo de finalização."
        )

        tipos_disponiveis = set(
            analise_tempo_finalizacao["tipoNegociacao"]
        )

        if not {"TROCA", "VENDA"}.issubset(tipos_disponiveis):
            logger.debug(
                "Insight de tempo de finalização não gerado: "
                "TROCA e VENDA não estão simultaneamente disponíveis."
            )
            return None

        troca = analise_tempo_finalizacao[
            analise_tempo_finalizacao["tipoNegociacao"] == "TROCA"
        ].iloc[0]

        venda = analise_tempo_finalizacao[
            analise_tempo_finalizacao["tipoNegociacao"] == "VENDA"
        ].iloc[0]

        tempo_troca = float(troca["tempoMedioDias"])
        tempo_venda = float(venda["tempoMedioDias"])

        if np.isclose(tempo_troca, tempo_venda):
            modalidade_mais_rapida = "EMPATE"
            mensagem = (
                "Trocas e vendas apresentaram o mesmo tempo médio histórico "
                "de finalização no período analisado."
            )

        elif tempo_troca < tempo_venda:
            modalidade_mais_rapida = "TROCA"
            mensagem = (
                "Trocas apresentaram menor tempo médio histórico de finalização "
                "do que vendas no período analisado."
            )

        else:
            modalidade_mais_rapida = "VENDA"
            mensagem = (
                "Vendas apresentaram menor tempo médio histórico de finalização "
                "do que trocas no período analisado."
            )

        insight = {
            "tipo": "TEMPO_FINALIZACAO",
            "titulo": "Tempo de finalização",
            "mensagem": mensagem,
            "dados": {
                "modalidadeMaisRapida": modalidade_mais_rapida,
                "tempoMedioDiasTroca": tempo_troca,
                "tempoMedioDiasVenda": tempo_venda,
                "diferencaTempoMedioDias": abs(
                    tempo_troca - tempo_venda
                ),
                "totalFinalizadasTroca": int(troca["totalFinalizadas"]),
                "totalFinalizadasVenda": int(venda["totalFinalizadas"]),
            }
        }

        logger.debug(
            "Insight de tempo de finalização gerado. "
            "Modalidade mais rápida: %s.",
            modalidade_mais_rapida
        )

        return insight

    def _gerar_insight_evolucao_temporal(
            self,
            negociacoes_por_mes: pd.DataFrame
    ) -> dict | None:
        """
        Gera um insight sobre a evolução recente do volume mensal
        de negociações iniciadas.

        A análise compara os dois períodos mensais mais recentes,
        identificando aumento, redução ou estabilidade no volume
        de negociações registradas.

        Args:
            negociacoes_por_mes: DataFrame contendo a quantidade
                de negociações iniciadas em cada mês.

        Returns:
            Dicionário contendo o insight de evolução temporal e
            os dados que sustentam a comparação, ou None quando
            não houver pelo menos dois períodos disponíveis.
        """
        logger.debug(
            "Iniciando geração do insight de evolução temporal."
        )

        if len(negociacoes_por_mes) < 2:
            logger.debug(
                "Insight de evolução temporal não gerado: "
                "são necessários pelo menos dois períodos."
            )
            return None

        periodos_ordenados = (
            negociacoes_por_mes
            .sort_values("mesNegociacao")
            .reset_index(drop=True)
        )

        periodo_anterior = periodos_ordenados.iloc[-2]
        periodo_atual = periodos_ordenados.iloc[-1]

        mes_anterior = str(periodo_anterior["mesNegociacao"])
        mes_atual = str(periodo_atual["mesNegociacao"])

        quantidade_anterior = int(periodo_anterior["quantidade"])
        quantidade_atual = int(periodo_atual["quantidade"])

        diferenca = quantidade_atual - quantidade_anterior

        if diferenca > 0:
            evolucao = "AUMENTO"
            mensagem = (
                f"O volume de negociações iniciadas aumentou em {mes_atual} "
                f"em relação a {mes_anterior}."
            )

        elif diferenca < 0:
            evolucao = "REDUCAO"
            mensagem = (
                f"O volume de negociações iniciadas diminuiu em {mes_atual} "
                f"em relação a {mes_anterior}."
            )

        else:
            evolucao = "ESTABILIDADE"
            mensagem = (
                f"O volume de negociações iniciadas permaneceu estável em "
                f"{mes_atual} em relação a {mes_anterior}."
            )

        if quantidade_anterior > 0:
            variacao_percentual = (
                diferenca / quantidade_anterior
            )
        else:
            variacao_percentual = None

        insight = {
            "tipo": "EVOLUCAO_TEMPORAL",
            "titulo": "Evolução mensal das negociações",
            "mensagem": mensagem,
            "dados": {
                "evolucao": evolucao,
                "mesAnterior": mes_anterior,
                "mesAtual": mes_atual,
                "quantidadeAnterior": quantidade_anterior,
                "quantidadeAtual": quantidade_atual,
                "diferencaQuantidade": abs(diferenca),
                "variacaoPercentual": variacao_percentual
            }
        }

        logger.debug(
            "Insight de evolução temporal gerado. "
            "Evolução: %s. Período: %s para %s.",
            evolucao,
            mes_anterior,
            mes_atual
        )

        return insight

    def _gerar_insight_afinidade(
            self,
            analise_afinidade: pd.DataFrame
    ) -> dict | None:
        """
        Gera um insight comparativo sobre a relação entre afinidade
        de categorias e finalização das negociações de troca.

        A análise compara as taxas históricas de finalização dos níveis
        de afinidade disponíveis, identificando aquele que apresentou
        maior taxa no período analisado.

        Args:
            analise_afinidade: DataFrame contendo os indicadores de
                finalização agrupados por nível de afinidade.

        Returns:
            Dicionário contendo o insight de afinidade e os dados que
            sustentam a comparação, ou None quando não houver níveis
            suficientes para realizar a comparação.
        """
        logger.debug(
            "Iniciando geração do insight de afinidade entre categorias."
        )

        if len(analise_afinidade) < 2:
            logger.debug(
                "Insight de afinidade não gerado: "
                "são necessários pelo menos dois níveis de afinidade."
            )
            return None

        maior_taxa = float(
            analise_afinidade["taxaFinalizacao"].max()
        )

        afinidades_destaque = analise_afinidade[
            np.isclose(
                analise_afinidade["taxaFinalizacao"],
                maior_taxa
            )
        ]

        if len(afinidades_destaque) == 1:
            afinidade_destaque = str(
                afinidades_destaque.iloc[0]["afinidade"]
            )

            mensagem = (
                f"Trocas com afinidade {afinidade_destaque} entre as categorias "
                "dos livros apresentaram a maior taxa histórica de finalização "
                "entre os níveis observados."
            )

            afinidades = [afinidade_destaque]

        else:
            afinidades = (
                afinidades_destaque["afinidade"]
                .astype(str)
                .tolist()
            )

            nomes_afinidades = ", ".join(afinidades)

            mensagem = (
                f"Os níveis de afinidade {nomes_afinidades} apresentaram a mesma "
                "maior taxa histórica de finalização entre os níveis observados."
            )

        dados_afinidades = []

        for _, linha in afinidades_destaque.iterrows():
            dados_afinidades.append({
                "afinidade": str(linha["afinidade"]),
                "totalNegociacoes": int(linha["totalNegociacoes"]),
                "totalFinalizadas": int(linha["totalFinalizadas"]),
                "taxaFinalizacao": float(linha["taxaFinalizacao"])
            })

        niveis_observados = (
            analise_afinidade["afinidade"]
            .astype(str)
            .tolist()
        )

        insight = {
            "tipo": "AFINIDADE",
            "titulo": "Afinidade entre categorias",
            "mensagem": mensagem,
            "dados": {
                "afinidadesDestaque": dados_afinidades,
                "niveisObservados": niveis_observados
            }
        }

        logger.debug(
            "Insight de afinidade gerado. "
            "Afinidades em destaque: %s.",
            afinidades
        )

        return insight

    def _gerar_insight_combinacoes_categorias(
            self,
            analise_combinacoes_ajustada: pd.DataFrame
    ) -> dict | None:
        """
        Gera um insight sobre as combinações de categorias com maior
        taxa histórica de finalização ajustada nas negociações de troca.

        A análise utiliza a taxa suavizada pelo modelo Beta-Binomial,
        reduzindo a influência de resultados extremos provenientes
        de combinações com poucas observações.

        Args:
            analise_combinacoes_ajustada: DataFrame contendo os indicadores
                históricos das combinações de categorias e suas taxas de
                finalização ajustadas.

        Returns:
            Dicionário contendo o insight das combinações em destaque
            e os dados que sustentam a interpretação, ou None quando
            não houver combinações disponíveis.
        """
        logger.debug(
            "Iniciando geração do insight por combinação de categorias."
        )

        if analise_combinacoes_ajustada.empty:
            logger.debug(
                "Insight por combinação de categorias não gerado: "
                "nenhuma combinação disponível."
            )
            return None

        maior_taxa_ajustada = float(
            analise_combinacoes_ajustada.iloc[0][
                "taxaFinalizacaoAjustada"
            ]
        )

        combinacoes_destaque = analise_combinacoes_ajustada[
            np.isclose(
                analise_combinacoes_ajustada["taxaFinalizacaoAjustada"],
                maior_taxa_ajustada
            )
        ]

        if len(combinacoes_destaque) == 1:
            combinacao_destaque = combinacoes_destaque.iloc[0]

            categoria_anuncio = str(
                combinacao_destaque["categoriaAnuncio"]
            )
            categoria_oferecida = str(
                combinacao_destaque["categoriaAnuncioOferecido"]
            )

            mensagem = (
                f"A combinação {categoria_anuncio} × {categoria_oferecida} "
                "apresentou a maior taxa histórica de finalização ajustada "
                "entre as combinações observadas nas trocas."
            )

        else:
            nomes_combinacoes = []

            for _, linha in combinacoes_destaque.iterrows():
                nomes_combinacoes.append(
                    f"{linha['categoriaAnuncio']} × "
                    f"{linha['categoriaAnuncioOferecido']}"
                )

            combinacoes_formatadas = ", ".join(nomes_combinacoes)

            mensagem = (
                f"As combinações {combinacoes_formatadas} apresentaram a mesma "
                "maior taxa histórica de finalização ajustada entre as "
                "combinações observadas nas trocas."
            )

        dados_combinacoes = []

        for _, linha in combinacoes_destaque.iterrows():
            dados_combinacoes.append({
                "categoriaAnuncio": str(linha["categoriaAnuncio"]),
                "categoriaAnuncioOferecido": str(
                    linha["categoriaAnuncioOferecido"]
                ),
                "totalNegociacoes": int(linha["totalNegociacoes"]),
                "totalFinalizadas": int(linha["totalFinalizadas"]),
                "taxaFinalizacao": float(linha["taxaFinalizacao"]),
                "taxaFinalizacaoAjustada": float(
                    linha["taxaFinalizacaoAjustada"]
                )
            })

        insight = {
            "tipo": "COMBINACAO_CATEGORIAS",
            "titulo": "Combinações de categorias nas trocas",
            "mensagem": mensagem,
            "dados": {
                "combinacoesDestaque": dados_combinacoes
            }
        }

        logger.debug(
            "Insight por combinação de categorias gerado. "
            "Combinações em destaque: %d.",
            len(dados_combinacoes)
        )

        return insight
