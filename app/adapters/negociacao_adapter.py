"""
Módulo de adaptação de dados de negociações para os formatos de resposta da API.
"""

from typing import Any
import pandas as pd

from app.controllers.responses.negociacao_response import NegociacaoResponse


class NegociacaoAdapter:
    """
    Responsável por transformar estruturas internas de negociações em objetos de resposta da API.
    """

    @staticmethod
    def _serializar_dataframe(df: Any) -> list[dict[str, Any]]:
        """Converte um Dataframe Pandas em lista de dicionários serializáveis."""
        if isinstance(df, pd.DataFrame):
            if df.empty:
                return []
            df_copia = df.copy()
            for col in df_copia.columns:
                if isinstance(df_copia[col].dtype, pd.PeriodDtype):
                    df_copia[col] = df_copia[col].astype(str)
            return df_copia.to_dict(orient="records")
        return []

    @classmethod
    def para_response(cls, resultado_service: dict[str, Any]) -> NegociacaoResponse:
        """
        Converte os dados de negociações calculados pelo serviço em um objeto NegociacaoResponse.

        Args:
            resultado_service: Dicionário contendo os indicadores de negociações.

        Returns:
            Instância de NegociacaoResponse formatada para a API.
        """
        geral = resultado_service.get("geral", {})
        temporal = resultado_service.get("temporal", {})

        return NegociacaoResponse(
            geral={
                "totalNegociacoes": geral.get("totalNegociacoes", 0),
                "negociacoesPorStatus": cls._serializar_dataframe(geral.get("negociacoesPorStatus")),
                "negociacoesPorTipo": cls._serializar_dataframe(geral.get("negociacoesPorTipo")),
            },
            porTipo=cls._serializar_dataframe(resultado_service.get("porTipo")),
            porCategoria=cls._serializar_dataframe(resultado_service.get("porCategoria")),
            afinidadeCategorias=cls._serializar_dataframe(resultado_service.get("afinidadeCategorias")),
            combinacoesCategorias=cls._serializar_dataframe(resultado_service.get("combinacoesCategorias")),
            temporal={
                "negociacoesPorMes": cls._serializar_dataframe(temporal.get("negociacoesPorMes")),
                "negociacoesPorMesTipo": cls._serializar_dataframe(temporal.get("negociacoesPorMesTipo")),
                "finalizacoesPorMes": cls._serializar_dataframe(temporal.get("finalizacoesPorMes")),
                "tempoFinalizacao": cls._serializar_dataframe(temporal.get("tempoFinalizacao")),
                "taxaFinalizacaoPorMesInicio": cls._serializar_dataframe(temporal.get("taxaFinalizacaoPorMesInicio")),
            },
            insights=resultado_service.get("insights", []),
        )