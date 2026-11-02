"""
Módulo de adaptação de dados de previsão temporal de usuários para os formatos de resposta da API.
"""

from typing import Any
import pandas as pd

from app.controllers.responses.previsao_temporal_response import PrevisaoTemporalResponse


class PrevisaoTemporalAdapter:
    """
    Responsável por transformar estruturas internas de previsão de usuários em objetos de resposta da API.
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
    def para_response(
        cls, resultado_service: dict[str, Any] | None
    ) -> PrevisaoTemporalResponse | None:
        """
        Converte o resultado da previsão temporal de usuários em um objeto PrevisaoTemporalResponse.

        Args:
            resultado_service: Dicionário retornado pela previsão temporal ou None.

        Returns:
            Instância de PrevisaoTemporalResponse ou None.
        """
        if not resultado_service:
            return PrevisaoTemporalResponse(
                avaliacao={
                    "mae": None,
                    "rmse": None,
                    "previsoesTeste": []
                },
                projecoes=[],
                resumoHorizontes=[],
                modelo={"status": "HISTORICO_INSUFICIENTE",
                        "mensagem": "Histórico de registros insuficiente para calcular projeção preditiva."}
            )

        avaliacao = resultado_service.get("avaliacao", {})

        return PrevisaoTemporalResponse(
            avaliacao={
                "mae": avaliacao.get("mae"),
                "rmse": avaliacao.get("rmse"),
                "previsoesTeste": cls._serializar_dataframe(avaliacao.get("previsoesTeste")),
            },
            projecoes=cls._serializar_dataframe(resultado_service.get("projecoes")),
            resumoHorizontes=cls._serializar_dataframe(resultado_service.get("resumoHorizontes")),
            modelo=resultado_service.get("modelo", {}),
        )