"""
Módulo de análise descritiva e diagnóstica dos anúncios do Trocabook.

A classe recebe registros já recuperados da fonte de dados, como documentos
do Firebase Cloud Firestore convertidos em dicionários, e retorna indicadores
e tabelas prontos para consumo por uma API ou dashboard administrativo.
"""

import logging
from collections.abc import Mapping, Sequence
from typing import Any

import pandas as pd


logger = logging.getLogger(__name__)


class AnuncioAnalytics:
    """Calcula indicadores de volume, distribuição, qualidade e evolução dos anúncios.

    Os registros podem ser dicionários ou objetos com atributos equivalentes.
    A classe não acessa diretamente o Firebase e não produz gráficos; retorna
    dados estruturados para que a camada de apresentação decida como exibi-los.
    """

    COLUNAS = [
        "id",
        "uidUsuario",
        "uidLivro",
        "titulo",
        "autores",
        "categorias",
        "tipoNegociacao",
        "dataCriacao",
    ]
    TIPOS_NEGOCIACAO = ("TROCA", "VENDA", "AMBOS")

    def analisar(self, anuncios: Sequence[Any] | None) -> dict[str, Any]:
        """Executa todas as análises disponíveis sobre os anúncios informados.

        Args:
            anuncios: Sequência de documentos de anúncio como dicionários ou
                objetos. Se for ``None`` ou vazia, será retornada a estrutura
                padronizada sem resultados.

        Returns:
            Dicionário com as chaves ``geral``, ``porTipo``, ``porAutor``,
            ``porCategoria``, ``categoriaPorTipo``, ``temporal`` e ``insights``.
            As distribuições e séries são representadas por DataFrames pandas.

        Raises:
            TypeError: Se ``anuncios`` não for uma sequência compatível com a
                conversão esperada ou se algum registro tiver estrutura inválida
                para os métodos de acesso utilizados.
        """
        quantidade_recebida = len(anuncios) if anuncios is not None else 0
        logger.info(
            "Iniciando análise de anúncios. Registros recebidos: %d.",
            quantidade_recebida,
        )

        dataframe = self._converter_anuncios_dataframe(anuncios or [])
        if dataframe.empty:
            logger.info("Análise de anúncios concluída sem dados disponíveis.")
            return self._resultado_vazio()

        dataframe = self._preparar_dados(dataframe)
        analise_geral = self._analisar_geral(dataframe)
        analise_tipo = self._analisar_por_tipo(dataframe)
        analise_autor = self._analisar_por_autor(dataframe)
        analise_categoria = self._analisar_por_categoria(dataframe)
        analise_categoria_tipo = self._analisar_categoria_por_tipo(dataframe)
        analise_temporal = self._analisar_temporal(dataframe)
        insights = self._gerar_insights(
            analise_geral,
            analise_tipo,
            analise_categoria,
            analise_temporal,
        )

        resultado = {
            "geral": analise_geral,
            "porTipo": analise_tipo,
            "porAutor": analise_autor,
            "porCategoria": analise_categoria,
            "categoriaPorTipo": analise_categoria_tipo,
            "temporal": analise_temporal,
            "insights": insights,
        }
        logger.info(
            "Análise de anúncios concluída. Registros analisados: %d. "
            "Insights gerados: %d.",
            len(dataframe),
            len(insights),
        )
        return resultado

    def _resultado_vazio(self) -> dict[str, Any]:
        """Cria a estrutura de retorno padrão quando não existem anúncios.

        Returns:
            Dicionário com todos os indicadores zerados, períodos nulos,
            DataFrames vazios com colunas definidas e lista de insights vazia.
        """
        logger.debug("Montando estrutura de retorno para análise sem anúncios.")
        return {
            "geral": {
                "totalAnuncios": 0,
                "totalUsuariosAnunciantes": 0,
                "totalLivros": 0,
                "periodoInicial": None,
                "periodoFinal": None,
                "anunciosSemAutores": 0,
                "anunciosSemCategorias": 0,
                "anunciosSemTipoNegociacao": 0,
                "anunciosComDataInvalida": 0,
                "quantidadeMesesAnalisados": 0,
            },
            "porTipo": pd.DataFrame(
                columns=["tipoNegociacao", "quantidadeAnuncios", "percentual"]
            ),
            "porAutor": pd.DataFrame(
                columns=["autor", "quantidadeAnuncios", "percentualAnuncios"]
            ),
            "porCategoria": pd.DataFrame(
                columns=["categoria", "quantidadeAnuncios", "percentualAnuncios"]
            ),
            "categoriaPorTipo": {
                "quantidades": pd.DataFrame(),
                "percentuais": pd.DataFrame(),
            },
            "temporal": {
                "anunciosPorMes": pd.DataFrame(
                    columns=["mesCriacao", "novosAnuncios", "variacaoPercentual"]
                ),
                "anunciosPorMesTipo": pd.DataFrame(
                    columns=["mesCriacao", "tipoNegociacao", "quantidadeAnuncios"]
                ),
                "evolucaoPorTipo": pd.DataFrame(),
                "resumoMensal": {
                    "quantidadeMeses": 0,
                    "menorQuantidade": None,
                    "maiorQuantidade": None,
                    "mediaMensal": None,
                    "maiorCrescimento": None,
                    "maiorReducao": None,
                },
            },
            "insights": [],
        }

    def _converter_anuncios_dataframe(
        self, anuncios: Sequence[Any]
    ) -> pd.DataFrame:
        """Converte registros em DataFrame com as colunas esperadas.

        Args:
            anuncios: Sequência de registros em formato de dicionário ou objeto.

        Returns:
            DataFrame contendo as colunas definidas em ``COLUNAS``. Campos
            ausentes são preenchidos com valores nulos para tratamento posterior.
        """
        logger.debug("Convertendo %d anúncios para DataFrame.", len(anuncios))
        registros = [
            {coluna: self._obter_valor(anuncio, coluna) for coluna in self.COLUNAS}
            for anuncio in anuncios
        ]
        dataframe = pd.DataFrame(registros, columns=self.COLUNAS)
        logger.debug("Conversão concluída. Registros no DataFrame: %d.", len(dataframe))
        return dataframe

    @staticmethod
    def _obter_valor(anuncio: Any, campo: str) -> Any:
        """Obtém o valor de um campo em um dicionário ou objeto.

        Args:
            anuncio: Registro de anúncio.
            campo: Nome do atributo ou chave a consultar.

        Returns:
            Valor encontrado ou ``None`` se o campo não existir.
        """
        if isinstance(anuncio, Mapping):
            return anuncio.get(campo)
        return getattr(anuncio, campo, None)

    def _preparar_dados(self, dataframe: pd.DataFrame) -> pd.DataFrame:
        """Normaliza listas, tipos de negociação e datas para as análises.

        Args:
            dataframe: DataFrame contendo as colunas de ``COLUNAS``.

        Returns:
            Cópia do DataFrame com ``autores`` e ``categorias`` normalizados,
            ``tipoNegociacao`` em maiúsculas, ``dataCriacao`` convertida para
            datetime e coluna auxiliar ``mesCriacao`` no formato período mensal.
        """
        logger.debug("Preparando dados dos anúncios. Registros recebidos: %d.", len(dataframe))
        dataframe = dataframe.copy()
        for coluna in ("autores", "categorias"):
            dataframe[coluna] = dataframe[coluna].apply(self._normalizar_lista)
        dataframe["tipoNegociacao"] = dataframe["tipoNegociacao"].apply(
            self._normalizar_tipo
        )
        dataframe["dataCriacao"] = pd.to_datetime(
            dataframe["dataCriacao"], errors="coerce", utc=True
        ).dt.tz_convert(None)
        dataframe["mesCriacao"] = dataframe["dataCriacao"].dt.to_period("M")
        logger.debug(
            "Preparação concluída. Datas válidas: %d; datas inválidas: %d.",
            int(dataframe["dataCriacao"].notna().sum()),
            int(dataframe["dataCriacao"].isna().sum()),
        )
        return dataframe

    @staticmethod
    def _normalizar_lista(valor: Any) -> list[Any]:
        """Converte um valor de autores/categorias em uma lista consistente.

        Args:
            valor: Valor original, que pode ser ``None``, texto ou sequência.

        Returns:
            Lista sem itens nulos ou textos vazios. Valores não suportados
            resultam em uma lista vazia.
        """
        if valor is None:
            return []
        if isinstance(valor, str):
            valor = valor.strip()
            return [valor] if valor else []
        if isinstance(valor, Sequence) and not isinstance(
            valor, (bytes, bytearray)
        ):
            return [
                item for item in valor
                if item is not None and str(item).strip()
            ]
        return []

    @staticmethod
    def _normalizar_tipo(valor: Any) -> str | None:
        """Normaliza o tipo de negociação, inclusive valores de Enum.

        Args:
            valor: Tipo original, texto, Enum ou valor nulo.

        Returns:
            Texto sem espaços externos e em maiúsculas, ou ``None`` se vazio.
        """
        if valor is None or pd.isna(valor):
            return None

        valor = getattr(valor, "value", valor)
        texto = str(valor).strip().upper()

        return texto or None

    def _analisar_geral(self, dataframe: pd.DataFrame) -> dict[str, Any]:
        """Calcula indicadores gerais e sinaliza campos incompletos ou inválidos.

        Args:
            dataframe: DataFrame já normalizado por ``_preparar_dados``.

        Returns:
            Dicionário com total de anúncios, usuários e livros distintos,
            período coberto, quantidade de anúncios sem autores/categorias/tipo,
            quantidade de datas inválidas e número de meses distintos.
        """
        logger.debug("Iniciando cálculo dos indicadores gerais dos anúncios.")
        datas_validas = dataframe["dataCriacao"].dropna()
        usuarios = dataframe["uidUsuario"].dropna()
        livros = dataframe["uidLivro"].dropna()
        ids_validos = dataframe["id"].dropna()
        meses_validos = dataframe["mesCriacao"].dropna()

        resultado = {
            "totalAnuncios": int(ids_validos.nunique()) if not ids_validos.empty else len(dataframe),
            "totalUsuariosAnunciantes": int(usuarios.nunique()),
            "totalLivros": int(livros.nunique()),
            "periodoInicial": datas_validas.min() if not datas_validas.empty else None,
            "periodoFinal": datas_validas.max() if not datas_validas.empty else None,
            "anunciosSemAutores": int(dataframe["autores"].apply(len).eq(0).sum()),
            "anunciosSemCategorias": int(dataframe["categorias"].apply(len).eq(0).sum()),
            "anunciosSemTipoNegociacao": int(dataframe["tipoNegociacao"].isna().sum()),
            "anunciosComDataInvalida": int(dataframe["dataCriacao"].isna().sum()),
            "quantidadeMesesAnalisados": int(meses_validos.nunique()),
        }
        logger.debug(
            "Indicadores gerais calculados. Anúncios: %d; usuários: %d; livros: %d.",
            resultado["totalAnuncios"],
            resultado["totalUsuariosAnunciantes"],
            resultado["totalLivros"],
        )
        return resultado

    def _analisar_por_tipo(self, dataframe: pd.DataFrame) -> pd.DataFrame:
        """Calcula quantidade e percentual dos anúncios por tipo de negociação.

        Args:
            dataframe: DataFrame de anúncios normalizado.

        Returns:
            DataFrame com ``tipoNegociacao``, ``quantidadeAnuncios`` e
            ``percentual``. O percentual usa o total de anúncios como denominador,
            conforme a metodologia do notebook.
        """
        logger.debug("Iniciando distribuição dos anúncios por tipo de negociação.")
        dados_validos = dataframe[dataframe["tipoNegociacao"].notna()]
        total = len(dataframe)
        distribuicao = (
            dados_validos["tipoNegociacao"]
            .value_counts()
            .rename_axis("tipoNegociacao")
            .reset_index(name="quantidadeAnuncios")
        )
        if distribuicao.empty:
            return pd.DataFrame(
                columns=["tipoNegociacao", "quantidadeAnuncios", "percentual"]
            )
        distribuicao["percentual"] = (
            distribuicao["quantidadeAnuncios"] / total * 100
        ).round(2) if total else 0.0
        logger.debug("Distribuição por tipo concluída. Tipos encontrados: %d.", len(distribuicao))
        return distribuicao

    def _analisar_por_autor(self, dataframe: pd.DataFrame) -> pd.DataFrame:
        """Calcula a presença dos autores nos anúncios.

        Cada associação anúncio-autor é contada individualmente. Um anúncio com
        mais de um autor contribui uma vez para cada autor associado.

        Args:
            dataframe: DataFrame de anúncios com ``autores`` normalizados.

        Returns:
            DataFrame ordenado por frequência, com ``autor``,
            ``quantidadeAnuncios`` e ``percentualAnuncios``. O percentual usa
            o total de anúncios como denominador, portanto pode somar mais de 100%.
        """
        logger.debug("Iniciando distribuição dos anúncios por autor.")
        total = len(dataframe)
        expandido = dataframe[["autores"]].explode("autores")
        expandido = expandido[expandido["autores"].notna()]
        resultado = (
            expandido["autores"]
            .value_counts()
            .rename_axis("autor")
            .reset_index(name="quantidadeAnuncios")
        )
        resultado["percentualAnuncios"] = (
            (resultado["quantidadeAnuncios"] / total * 100).round(2)
            if total else 0.0
        )
        logger.debug("Distribuição por autor concluída. Itens encontrados: %d.", len(resultado))
        return resultado

    def _analisar_por_categoria(self, dataframe: pd.DataFrame) -> pd.DataFrame:
        """Calcula a frequência e participação de cada categoria nos anúncios.

        Args:
            dataframe: DataFrame de anúncios com ``categorias`` normalizadas.

        Returns:
            DataFrame ordenado por frequência, com ``categoria``,
            ``quantidadeAnuncios`` e ``percentualAnuncios``. Como um anúncio
            pode ter várias categorias, os percentuais podem somar mais de 100%.
        """
        logger.debug("Iniciando distribuição dos anúncios por categoria.")
        total = len(dataframe)
        expandido = dataframe[["categorias"]].explode("categorias")
        expandido = expandido[expandido["categorias"].notna()]
        resultado = (
            expandido["categorias"]
            .value_counts()
            .rename_axis("categoria")
            .reset_index(name="quantidadeAnuncios")
        )
        resultado["percentualAnuncios"] = (
            (resultado["quantidadeAnuncios"] / total * 100).round(2)
            if total else 0.0
        )
        logger.debug("Distribuição por categoria concluída. Itens encontrados: %d.", len(resultado))
        return resultado

    def _analisar_categoria_por_tipo(self, dataframe: pd.DataFrame) -> dict[str, pd.DataFrame]:
        """Cruza categorias e tipos de negociação em contagens e percentuais.

        Args:
            dataframe: DataFrame de anúncios com categorias e tipos normalizados.

        Returns:
            Dicionário com os DataFrames ``quantidades`` e ``percentuais``.
            As linhas representam categorias e as colunas os tipos TROCA, VENDA
            e AMBOS; os percentuais são calculados dentro de cada categoria.
        """
        logger.debug("Iniciando cruzamento entre categorias e tipos de negociação.")
        expandido = dataframe[["categorias", "tipoNegociacao"]].explode("categorias").reset_index(drop=True)
        expandido = expandido[
            expandido["categorias"].notna() & expandido["tipoNegociacao"].notna()
        ]
        if expandido.empty:
            return {"quantidades": pd.DataFrame(), "percentuais": pd.DataFrame()}

        quantidades = pd.crosstab(
            expandido["categorias"], expandido["tipoNegociacao"]
        ).astype(int)
        quantidades.index.name = "categoria"
        quantidades = quantidades.reindex(columns=self.TIPOS_NEGOCIACAO, fill_value=0)
        totais = quantidades.sum(axis=1).replace(0, pd.NA)
        percentuais = quantidades.div(totais, axis=0).mul(100).fillna(0).round(2)
        percentuais.index.name = "categoria"
        logger.debug("Cruzamento categoria/tipo concluído. Categorias analisadas: %d.", len(quantidades))
        return {"quantidades": quantidades, "percentuais": percentuais}

    def _analisar_temporal(self, dataframe: pd.DataFrame) -> dict[str, Any]:
        """Calcula volume mensal, variação percentual e evolução por modalidade.

        Args:
            dataframe: DataFrame de anúncios com ``dataCriacao`` e ``mesCriacao``
                normalizados.

        Returns:
            Dicionário contendo ``anunciosPorMes``, ``anunciosPorMesTipo``,
            ``evolucaoPorTipo`` e ``resumoMensal``. Meses sem anúncios não são
            interpolados: somente meses presentes nos dados são retornados.
        """
        logger.debug("Iniciando análise temporal dos anúncios.")
        dados_validos = dataframe[dataframe["mesCriacao"].notna()].copy()
        if dados_validos.empty:
            return self._resultado_vazio()["temporal"]

        por_mes = (
            dados_validos.groupby("mesCriacao")
            .size()
            .rename("novosAnuncios")
            .reset_index()
            .sort_values("mesCriacao")
            .reset_index(drop=True)
        )
        por_mes["variacaoPercentual"] = (
            por_mes["novosAnuncios"].pct_change().mul(100).round(2)
        )

        por_mes_tipo = (
            dados_validos[dados_validos["tipoNegociacao"].notna()]
            .groupby(["mesCriacao", "tipoNegociacao"])
            .size()
            .reset_index(name="quantidadeAnuncios")
            .sort_values(["mesCriacao", "tipoNegociacao"])
            .reset_index(drop=True)
        )

        if por_mes_tipo.empty:
            evolucao = pd.DataFrame(
                index=pd.Index(por_mes["mesCriacao"], name="mesCriacao")
            )
        else:
            evolucao = por_mes_tipo.pivot(
                index="mesCriacao",
                columns="tipoNegociacao",
                values="quantidadeAnuncios",
            ).fillna(0).astype(int)
            evolucao = evolucao.reindex(columns=self.TIPOS_NEGOCIACAO, fill_value=0)
            evolucao = evolucao.reindex(por_mes["mesCriacao"], fill_value=0)
            evolucao.columns.name = "tipoNegociacao"

        variacoes = por_mes.dropna(subset=["variacaoPercentual"])
        crescimento = variacoes.loc[variacoes["variacaoPercentual"].idxmax()] if not variacoes.empty else None
        reducao = variacoes.loc[variacoes["variacaoPercentual"].idxmin()] if not variacoes.empty else None
        resumo = {
            "quantidadeMeses": int(len(por_mes)),
            "menorQuantidade": int(por_mes["novosAnuncios"].min()),
            "maiorQuantidade": int(por_mes["novosAnuncios"].max()),
            "mediaMensal": round(float(por_mes["novosAnuncios"].mean()), 2),
            "maiorCrescimento": (
                {"mesCriacao": crescimento["mesCriacao"],
                 "variacaoPercentual": float(crescimento["variacaoPercentual"])}
                if crescimento is not None and crescimento["variacaoPercentual"] > 0
                else None
            ),
            "maiorReducao": (
                {"mesCriacao": reducao["mesCriacao"],
                 "variacaoPercentual": float(reducao["variacaoPercentual"])}
                if reducao is not None and reducao["variacaoPercentual"] < 0
                else None
            ),
        }
        logger.debug("Análise temporal concluída. Meses: %d; registros temporais: %d.", len(por_mes), len(dados_validos))
        return {
            "anunciosPorMes": por_mes,
            "anunciosPorMesTipo": por_mes_tipo,
            "evolucaoPorTipo": evolucao,
            "resumoMensal": resumo,
        }

    def _gerar_insights(
        self,
        geral: dict[str, Any],
        por_tipo: pd.DataFrame,
        por_categoria: pd.DataFrame,
        temporal: dict[str, Any],
    ) -> list[str]:
        """Gera mensagens interpretáveis a partir dos indicadores disponíveis.

        Args:
            geral: Indicadores gerais calculados pela análise.
            por_tipo: Distribuição dos anúncios por modalidade de negociação.
            por_categoria: Distribuição dos anúncios por categoria.
            temporal: Indicadores e séries temporais calculados.

        Returns:
            Lista de mensagens. Insights para distribuições vazias ou séries sem
            variações válidas são omitidos para evitar conclusões sem evidência.
        """
        logger.debug("Iniciando geração de insights dos anúncios.")
        insights = []
        if not por_categoria.empty:
            destaque = por_categoria.iloc[0]
            insights.append(
                f"A categoria com maior presença é {destaque['categoria']}, "
                f"associada a {destaque['percentualAnuncios']:.2f}% dos anúncios."
            )
        if not por_tipo.empty:
            destaque = por_tipo.iloc[0]
            insights.append(
                f"A modalidade mais frequente é {destaque['tipoNegociacao']}, "
                f"representando {destaque['percentual']:.2f}% dos anúncios."
            )

        resumo = temporal.get("resumoMensal", {})
        crescimento = resumo.get("maiorCrescimento")
        reducao = resumo.get("maiorReducao")
        if crescimento:
            insights.append(
                f"O maior crescimento mensal ocorreu em {crescimento['mesCriacao']}, "
                f"com aumento de {crescimento['variacaoPercentual']:.2f}%."
            )
        if reducao:
            insights.append(
                f"A maior redução mensal ocorreu em {reducao['mesCriacao']}, "
                f"com queda de {abs(reducao['variacaoPercentual']):.2f}%."
            )
        if geral["totalAnuncios"] > 0:
            insights.append(
                f"Foram analisados {geral['totalAnuncios']} anúncios, publicados por "
                f"{geral['totalUsuariosAnunciantes']} usuários e associados a "
                f"{geral['totalLivros']} livros distintos."
            )
        logger.debug("Geração de insights concluída. Total de insights: %d.", len(insights))
        return insights
