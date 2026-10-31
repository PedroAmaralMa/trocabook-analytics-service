from fastapi.testclient import TestClient

from app.main import app
from app.exceptions.analytics_exception import AnalyticsException
from app.services.trocabook_analytics_service import TrocabookAnalyticsService


client = TestClient(app)


def test_root_deve_retornar_status_ok():
    response = client.get("/")

    assert response.status_code == 200
    assert response.json() == {"message": "Trocabook - Serviço de Analytics"}


def test_analisar_anuncios_sucesso():
    payload = {
        "anuncios": [
            {
                "id": "A1",
                "uidLivro": "L1",
                "uidUsuario": "U1",
                "titulo": "Dom Casmurro",
                "autores": ["Machado de Assis"],
                "categorias": ["Romance"],
                "tipoNegociacao": "TROCA",
                "status": "ATIVO",
                "dataCriacao": "2024-01-15T10:00:00",
            },
            {
                "id": "A2",
                "uidLivro": "L2",
                "uidUsuario": "U2",
                "titulo": "O Cortiço",
                "autores": ["Aluísio Azevedo"],
                "categorias": ["Romance"],
                "tipoNegociacao": "TROCA",
                "status": "ATIVO",
                "dataCriacao": "2024-02-15T10:00:00",
            },
            {
                "id": "A3",
                "uidLivro": "L3",
                "uidUsuario": "U3",
                "titulo": "Memórias Póstumas",
                "autores": ["Machado de Assis"],
                "categorias": ["Romance"],
                "tipoNegociacao": "TROCA",
                "status": "ATIVO",
                "dataCriacao": "2024-03-15T10:00:00",
            },
        ],
        "horizontePrevisao": 12,
        "quantidadeTeste": 1,
    }

    response = client.post("/analytics/anuncios", json=payload)

    assert response.status_code == 200

    dados = response.json()
    assert "analise" in dados
    assert "previsao" in dados
    assert dados["analise"]["geral"]["totalAnuncios"] == 3
    assert dados["previsao"] is not None

def test_analisar_anuncios_payload_vazio():
    payload = {"anuncios": []}

    response = client.post("/analytics/anuncios", json=payload)

    assert response.status_code == 200

    dados = response.json()
    assert dados["analise"]["geral"]["totalAnuncios"] == 0
    assert dados["previsao"] is None


def test_analisar_anuncios_retorna_422_quando_parametro_invalido():
    payload = {
        "anuncios": [],
        "horizontePrevisao": 0,
    }

    response = client.post("/analytics/anuncios", json=payload)

    assert response.status_code == 422


def test_analisar_negociacoes_sucesso():
    payload = {
        "negociacoes": [
            {
                "id": "N1",
                "anuncioId": "A1",
                "anuncioOferecidoId": "A2",
                "categoriasAnuncio": ["Ficção"],
                "categoriasAnuncioOferecido": ["Aventura"],
                "dataNegociacao": "2024-01-10T10:00:00",
                "dataFinalizacao": "2024-01-12T10:00:00",
                "tipoNegociacao": "TROCA",
                "status": "FINALIZADA",
            }
        ]
    }

    response = client.post("/analytics/negociacoes", json=payload)

    assert response.status_code == 200

    dados = response.json()
    assert "geral" in dados
    assert dados["geral"]["totalNegociacoes"] == 1


def test_analisar_negociacoes_payload_vazio():
    payload = {"negociacoes": []}

    response = client.post("/analytics/negociacoes", json=payload)

    assert response.status_code == 200

    dados = response.json()
    assert dados["geral"]["totalNegociacoes"] == 0


def test_gerar_previsao_temporal_usuarios_insuficiente():
    payload = {
        "usuarios": [
            {"id": "U1", "dataCriacao": "2024-01-01T00:00:00"}
        ],
        "horizontePrevisao": 12,
        "quantidadeTeste": 6,
    }

    response = client.post("/analytics/previsao-temporal", json=payload)

    assert response.status_code == 200
    assert response.json() is None


def test_gerar_previsao_temporal_usuarios_retorna_422_quando_parametro_invalido():
    payload = {
        "usuarios": [],
        "quantidadeTeste": -1,
    }

    response = client.post("/analytics/previsao-temporal", json=payload)

    assert response.status_code == 422


def test_deve_retornar_500_quando_analytics_exception_for_lancada(monkeypatch):
    def simular_erro(*args, **kwargs):
        raise AnalyticsException("Erro interno no processamento de analytics")

    monkeypatch.setattr(
        TrocabookAnalyticsService,
        "analisar_anuncios",
        simular_erro,
    )

    payload = {"anuncios": []}

    response = client.post("/analytics/anuncios", json=payload)

    assert response.status_code == 500
    assert response.json() == {
        "detail": "Erro interno no processamento de analytics"
    }