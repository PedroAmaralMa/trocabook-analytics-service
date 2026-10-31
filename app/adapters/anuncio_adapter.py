"""
Módulo de adaptação de dados de análise de anúncios para os formatos de resposta da API.
"""

from typing import Any
import pandas as pd

from app.adapters.previsao_temporal_adapter import PrevisaoTemporalAdapter
from app.controllers.responses.anuncio_response import (
    AnuncioAnaliseResponse,
    AnuncioResponse,
)
from app.controllers.responses.previsao_temporal_response import PrevisaoTemporalResponse


class AnuncioAdapter:
    """
    Responsável por transformar estruturas internas de análise de anúncios em objetos de resposta da API.
    """

    @staticmethod
    def _serializar_dataframe(df: Any) -> list[dict[str, Any]]:
        """Converte um Dataframe Pandas contendo Periods em lista de dicionários serializáveis."""
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
    def _preparar_previsao(cls, dados_previsao: dict[str, Any] | None) -> PrevisaoTemporalResponse | None:
        """Converte a previsão interna no DTO PrevisaoTemporalResponse."""
        if not dados_previsao:
            return None


        return PrevisaoTemporalAdapter.para_response(dados_previsao)

    @classmethod
    def para_response(cls, resultado_service: dict[str, Any]) -> AnuncioResponse:
        """
        Converte os dados brutos calculados pelo serviço em um objeto AnuncioResponse.

        Args:
            resultado_service: Dicionário contendo as chaves 'analise' e 'previsao'.

        Returns:
            Instância de AnuncioResponse formatada para a API.
        """
        analise_bruta = resultado_service.get("analise", {})
        previsao_bruta = resultado_service.get("previsao")

        categoria_por_tipo = analise_bruta.get("categoriaPorTipo", {})
        temporal = analise_bruta.get("temporal", {})

        analise_response = AnuncioAnaliseResponse(
            geral=analise_bruta.get("geral", {}),
            porTipo=cls._serializar_dataframe(analise_bruta.get("porTipo")),
            porAutor=cls._serializar_dataframe(analise_bruta.get("porAutor")),
            porCategoria=cls._serializar_dataframe(analise_bruta.get("porCategoria")),
            categoriaPorTipo={
                "quantidades": cls._serializar_dataframe(categoria_por_tipo.get("quantidades")),
                "percentuais": cls._serializar_dataframe(categoria_por_tipo.get("percentuais")),
            },
            temporal={
                "anunciosPorMes": cls._serializar_dataframe(temporal.get("anunciosPorMes")),
                "anunciosPorMesTipo": cls._serializar_dataframe(temporal.get("anunciosPorMesTipo")),
                "evolucaoPorTipo": cls._serializar_dataframe(temporal.get("evolucaoPorTipo")),
                "resumoMensal": temporal.get("resumoMensal", {}),
            },
            insights=analise_bruta.get("insights", []),
        )

        previsao_response = cls._preparar_previsao(previsao_bruta)

        return AnuncioResponse(
            analise=analise_response,
            previsao=previsao_response,
        )