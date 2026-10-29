"""
Módulo responsável pela previsão temporal de indicadores do Trocabook.

A classe utiliza regressão linear para projetar séries mensais de contagens,
como novos usuários e novos anúncios. A preparação dos dados de origem é de
responsabilidade do serviço que consome este módulo.
"""

import logging

import numpy as np
import pandas as pd

from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error


logger = logging.getLogger(__name__)


class PrevisaoTemporalAnalytics:
    """
    Responsável pela avaliação e previsão de séries temporais mensais.

    A classe recebe um DataFrame com um período mensal e uma métrica numérica.
    Dessa forma, a mesma implementação pode ser utilizada para prever novos
    usuários, novos anúncios ou outras contagens mensais da plataforma.
    """

    def prever(
        self,
        serie_mensal: pd.DataFrame,
        coluna_periodo: str = "mesCriacao",
        coluna_valor: str = "quantidade",
        horizonte: int = 12,
        quantidade_teste: int = 6
    ) -> dict:
        """
        Avalia a regressão linear e gera projeções para períodos futuros.

        Os últimos períodos da série são separados para avaliar o modelo. Em
        seguida, uma nova instância da regressão linear é treinada com todo o
        histórico disponível para produzir as projeções futuras.

        Args:
            serie_mensal: DataFrame com uma linha por mês e a métrica observada.
            coluna_periodo: Nome da coluna que identifica o mês de referência.
            coluna_valor: Nome da coluna com a quantidade observada no mês.
            horizonte: Quantidade de meses futuros a serem projetados.
            quantidade_teste: Quantidade de meses finais reservados para avaliação.

        Returns:
            Dicionário contendo métricas de avaliação, previsões do conjunto de
            teste, projeções futuras, resumo por horizonte e parâmetros do modelo.

        Raises:
            TypeError: Se a entrada ou os parâmetros possuírem tipos inválidos.
            ValueError: Se a série ou os parâmetros não atenderem aos requisitos.
        """
        logger.info(
            "Iniciando previsão temporal. Registros recebidos: %d.",
            len(serie_mensal) if isinstance(serie_mensal, pd.DataFrame) else 0
        )

        self._validar_parametros(
            serie_mensal,
            coluna_periodo,
            coluna_valor,
            horizonte,
            quantidade_teste
        )

        serie_preparada = self._preparar_serie_temporal(
            serie_mensal,
            coluna_periodo,
            coluna_valor
        )

        self._validar_quantidade_historico(
            serie_preparada,
            quantidade_teste
        )

        avaliacao = self._avaliar_regressao(
            serie_preparada,
            quantidade_teste
        )

        modelo_final = self._treinar_modelo_final(serie_preparada)

        projecoes = self._gerar_projecoes(
            serie_preparada,
            modelo_final,
            horizonte
        )

        resumo_horizontes = self._resumir_horizontes(projecoes)

        resultado = {
            "avaliacao": avaliacao,
            "projecoes": projecoes,
            "resumoHorizontes": resumo_horizontes,
            "modelo": {
                "coeficiente": float(modelo_final.coef_[0]),
                "intercepto": float(modelo_final.intercept_)
            }
        }

        logger.info(
            "Previsão temporal concluída. Meses históricos: %d. "
            "Meses projetados: %d.",
            len(serie_preparada),
            len(projecoes)
        )

        return resultado

    def _validar_parametros(
        self,
        serie_mensal: pd.DataFrame,
        coluna_periodo: str,
        coluna_valor: str,
        horizonte: int,
        quantidade_teste: int
    ) -> None:
        """
        Valida a estrutura da entrada e os parâmetros da previsão.

        Args:
            serie_mensal: Dados mensais recebidos para análise.
            coluna_periodo: Nome da coluna de período.
            coluna_valor: Nome da coluna de valores.
            horizonte: Quantidade de meses futuros solicitados.
            quantidade_teste: Quantidade de meses reservados para avaliação.

        Raises:
            TypeError: Se os tipos dos argumentos forem inválidos.
            ValueError: Se faltarem colunas ou se os parâmetros forem inválidos.
        """
        if not isinstance(serie_mensal, pd.DataFrame):
            raise TypeError("A série mensal deve ser um DataFrame do Pandas.")

        if not isinstance(coluna_periodo, str) or not coluna_periodo.strip():
            raise TypeError("O nome da coluna de período deve ser uma string não vazia.")

        if not isinstance(coluna_valor, str) or not coluna_valor.strip():
            raise TypeError("O nome da coluna de valores deve ser uma string não vazia.")

        if coluna_periodo == coluna_valor:
            raise ValueError("As colunas de período e de valores devem ser diferentes.")

        if isinstance(horizonte, bool) or not isinstance(horizonte, int):
            raise TypeError("O horizonte deve ser um número inteiro.")

        if isinstance(quantidade_teste, bool) or not isinstance(quantidade_teste, int):
            raise TypeError("A quantidade de teste deve ser um número inteiro.")

        if horizonte < 1:
            raise ValueError("O horizonte deve ser maior ou igual a 1 mês.")

        if quantidade_teste < 1:
            raise ValueError("A quantidade de teste deve ser maior ou igual a 1 mês.")

        colunas_necessarias = {coluna_periodo, coluna_valor}
        colunas_ausentes = colunas_necessarias.difference(serie_mensal.columns)

        if colunas_ausentes:
            raise ValueError(
                "Colunas obrigatórias ausentes: "
                + ", ".join(sorted(colunas_ausentes))
            )

    def _preparar_serie_temporal(
        self,
        serie_mensal: pd.DataFrame,
        coluna_periodo: str,
        coluna_valor: str
    ) -> pd.DataFrame:
        """
        Normaliza, ordena e completa a série mensal recebida.

        Os meses sem registros são preenchidos com zero, seguindo a preparação
        temporal utilizada nos experimentos de usuários e anúncios. A série
        resultante possui um índice temporal contínuo e um índice numérico para
        a regressão linear.

        Args:
            serie_mensal: DataFrame original com períodos e valores observados.
            coluna_periodo: Nome da coluna que identifica o mês.
            coluna_valor: Nome da coluna que contém a contagem mensal.

        Returns:
            DataFrame com as colunas mes, quantidade e indiceTempo.

        Raises:
            ValueError: Se os períodos ou valores forem inválidos ou duplicados.
        """
        logger.debug("Preparando série temporal mensal.")

        serie = serie_mensal[[coluna_periodo, coluna_valor]].copy()

        if serie.empty:
            raise ValueError("A série mensal não pode estar vazia.")

        try:
            valores_periodo = serie[coluna_periodo]

            if isinstance(valores_periodo.dtype, pd.PeriodDtype):
                serie["mes"] = valores_periodo.dt.asfreq("M")
            else:
                serie["mes"] = pd.PeriodIndex(
                    pd.to_datetime(valores_periodo, errors="raise"),
                    freq="M"
                )
        except (TypeError, ValueError, OverflowError) as erro:
            raise ValueError(
                "A coluna de período deve conter datas ou meses válidos."
            ) from erro

        if serie["mes"].isna().any():
            raise ValueError("A série contém períodos ausentes ou inválidos.")

        if serie["mes"].duplicated().any():
            raise ValueError("A série deve conter apenas um registro por mês.")

        try:
            serie["quantidade"] = pd.to_numeric(
                serie[coluna_valor],
                errors="raise"
            )
        except (TypeError, ValueError) as erro:
            raise ValueError("A métrica deve conter apenas valores numéricos.") from erro

        valores = serie["quantidade"].to_numpy(dtype=float)

        if not np.isfinite(valores).all():
            raise ValueError("A métrica não pode conter valores ausentes ou infinitos.")

        if (valores < 0).any():
            raise ValueError("A métrica de contagem não pode conter valores negativos.")

        serie = serie[["mes", "quantidade"]].sort_values("mes")

        periodos_completos = pd.period_range(
            start=serie["mes"].min(),
            end=serie["mes"].max(),
            freq="M"
        )

        serie = (
            serie.set_index("mes")
            .reindex(periodos_completos, fill_value=0)
            .rename_axis("mes")
            .reset_index()
        )

        valores = serie["quantidade"].to_numpy(dtype=float)

        if not np.isfinite(valores).all():
            raise ValueError(
                "A métrica não pode conter valores ausentes ou infinitos."
            )

        if (valores < 0).any():
            raise ValueError(
                "A métrica de contagem não pode conter valores negativos."
            )

        if not np.equal(valores, np.floor(valores)).all():
            raise ValueError(
                "A métrica de contagem deve conter valores inteiros."
            )

        serie["indiceTempo"] = np.arange(len(serie)).astype(int)
        serie["quantidade"] = serie["quantidade"].astype(int)

        logger.debug(
            "Série temporal preparada. Períodos contínuos: %d.",
            len(serie)
        )

        return serie

    def _validar_quantidade_historico(
        self,
        serie_mensal: pd.DataFrame,
        quantidade_teste: int
    ) -> None:
        """
        Garante que haja dados suficientes para treinamento e avaliação.

        Args:
            serie_mensal: Série mensal já normalizada.
            quantidade_teste: Quantidade de meses reservados para teste.

        Raises:
            ValueError: Se não houver ao menos dois meses para treinamento e
                um número suficiente de meses para avaliação.
        """
        quantidade_treino = len(serie_mensal) - quantidade_teste

        if quantidade_treino < 2:
            raise ValueError(
                "A série deve conter ao menos dois meses para treinamento, "
                "além dos meses reservados para teste."
            )

        logger.debug(
            "Histórico validado. Treinamento: %d meses; teste: %d meses.",
            quantidade_treino,
            quantidade_teste
        )

    def _avaliar_regressao(
        self,
        serie_mensal: pd.DataFrame,
        quantidade_teste: int
    ) -> dict:
        """
        Avalia a regressão linear utilizando os meses finais como teste.

        O modelo é treinado somente com os períodos anteriores ao conjunto de
        teste, preservando a ordem temporal adotada nos experimentos.

        Args:
            serie_mensal: Série mensal normalizada.
            quantidade_teste: Quantidade de meses finais para avaliação.

        Returns:
            Dicionário com MAE, RMSE e DataFrame contendo valores reais e previstos.
        """
        logger.debug("Iniciando avaliação da regressão linear.")

        treino = serie_mensal.iloc[:-quantidade_teste].copy()
        teste = serie_mensal.iloc[-quantidade_teste:].copy()

        modelo = LinearRegression()
        modelo.fit(treino[["indiceTempo"]], treino["quantidade"])

        previsoes = modelo.predict(teste[["indiceTempo"]])

        resultado_teste = teste[["mes", "quantidade"]].copy()
        resultado_teste["previsao"] = previsoes
        resultado_teste["previsao"] = resultado_teste["previsao"].clip(lower=0)

        mae = mean_absolute_error(
            resultado_teste["quantidade"],
            resultado_teste["previsao"]
        )
        rmse = np.sqrt(mean_squared_error(
            resultado_teste["quantidade"],
            resultado_teste["previsao"]
        ))

        logger.debug(
            "Avaliação concluída. MAE: %.4f; RMSE: %.4f.",
            mae,
            rmse
        )

        return {
            "mae": float(mae),
            "rmse": float(rmse),
            "previsoesTeste": resultado_teste.reset_index(drop=True)
        }

    def _treinar_modelo_final(
        self,
        serie_mensal: pd.DataFrame
    ) -> LinearRegression:
        """
        Treina a regressão linear com todo o histórico disponível.

        Args:
            serie_mensal: Série mensal normalizada.

        Returns:
            Modelo de regressão linear ajustado a todos os meses observados.
        """
        logger.debug("Treinando modelo final com todo o histórico.")

        modelo = LinearRegression()
        modelo.fit(serie_mensal[["indiceTempo"]], serie_mensal["quantidade"])

        logger.debug(
            "Modelo final treinado. Coeficiente: %.4f; intercepto: %.4f.",
            modelo.coef_[0],
            modelo.intercept_
        )

        return modelo

    def _gerar_projecoes(
        self,
        serie_mensal: pd.DataFrame,
        modelo: LinearRegression,
        horizonte: int
    ) -> pd.DataFrame:
        """
        Gera a projeção mensal para o horizonte solicitado.

        As projeções são limitadas a zero para evitar contagens negativas. A
        coluna quantidadeEstimada mantém valores inteiros, enquanto
        quantidadePrevista preserva o valor numérico produzido pelo modelo.

        Args:
            serie_mensal: Série mensal histórica normalizada.
            modelo: Regressão linear treinada com o histórico completo.
            horizonte: Quantidade de meses futuros a projetar.

        Returns:
            DataFrame com mês futuro, índice temporal e previsões estimadas.
        """
        logger.debug("Gerando projeções para %d meses futuros.", horizonte)

        ultimo_indice = int(serie_mensal["indiceTempo"].iloc[-1])
        indices_futuros = np.arange(
            ultimo_indice + 1,
            ultimo_indice + horizonte + 1
        )

        previsoes = modelo.predict(
            pd.DataFrame({"indiceTempo": indices_futuros})
        )
        previsoes = np.clip(previsoes, 0, None)

        ultimo_mes = serie_mensal["mes"].iloc[-1]
        meses_futuros = pd.period_range(
            start=ultimo_mes + 1,
            periods=horizonte,
            freq="M"
        )

        projecoes = pd.DataFrame({
            "mes": meses_futuros,
            "indiceTempo": indices_futuros,
            "quantidadePrevista": previsoes
        })
        projecoes["quantidadeEstimada"] = (
            projecoes["quantidadePrevista"].round().astype(int)
        )

        logger.debug("Projeções geradas: %d meses.", len(projecoes))

        return projecoes

    def _resumir_horizontes(
        self,
        projecoes: pd.DataFrame
    ) -> pd.DataFrame:
        """
        Consolida as projeções para os horizontes de 1, 3, 6 e 12 meses.

        Cada total corresponde à soma das quantidades previstas até o fim do
        horizonte. Apenas horizontes integralmente disponíveis na projeção são
        incluídos no resumo.

        Args:
            projecoes: DataFrame com as projeções mensais futuras.

        Returns:
            DataFrame com o total estimado para cada horizonte disponível.
        """
        logger.debug("Calculando resumo dos horizontes de previsão.")

        horizontes = [
            horizonte
            for horizonte in (1, 3, 6, 12)
            if horizonte <= len(projecoes)
        ]

        resumo = pd.DataFrame({
            "horizonteMeses": horizontes,
            "quantidadePrevista": [
                float(projecoes["quantidadePrevista"].iloc[:horizonte].sum())
                for horizonte in horizontes
            ]
        })

        resumo["quantidadeEstimada"] = (
            resumo["quantidadePrevista"].round().astype(int)
        )

        logger.debug(
            "Resumo dos horizontes concluído. Horizontes incluídos: %d.",
            len(resumo)
        )

        return resumo
