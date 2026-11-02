"""
Módulo de adaptação de dados de análise de anúncios para os formatos de resposta da API.
"""

from typing import Any
import pandas as pd
from app.controllers.responses.anuncio_response import AnuncioAnaliseResponse, AnuncioResponse
from app.adapters.previsao_temporal_adapter import PrevisaoTemporalAdapter

class AnuncioAdapter:
    @staticmethod
    def _serializar_dataframe(df: Any) -> list[dict[str, Any]]:
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
    def para_response(cls, resultado_service: dict[str, Any]) -> AnuncioResponse:
        analise = resultado_service.get("analise", {})
        previsao = resultado_service.get("previsao")

        temporal = analise.get("temporal", {})
        temporal_dto = {
            "anunciosPorMes": cls._serializar_dataframe(temporal.get("anunciosPorMes")),
            "anunciosPorMesTipo": cls._serializar_dataframe(temporal.get("anunciosPorMesTipo")),
            "evolucaoPorTipo": cls._serializar_dataframe(temporal.get("evolucaoPorTipo")),
            "resumoMensal": temporal.get("resumoMensal", {})
        }

        analise_dto = AnuncioAnaliseResponse(
            geral=analise.get("geral", {}),
            porTipo=cls._serializar_dataframe(analise.get("porTipo")),
            porAutor=cls._serializar_dataframe(analise.get("porAutor")),
            porCategoria=cls._serializar_dataframe(analise.get("porCategoria")),
            categoriaPorTipo={
                "quantidades": cls._serializar_dataframe(analise.get("categoriaPorTipo", {}).get("quantidades")),
                "percentuais": cls._serializar_dataframe(analise.get("categoriaPorTipo", {}).get("percentuais"))
            },
            temporal=temporal_dto,
            insights=analise.get("insights", [])
        )

        return AnuncioResponse(
            analise=analise_dto,
            previsao=PrevisaoTemporalAdapter.para_response(previsao)
        )