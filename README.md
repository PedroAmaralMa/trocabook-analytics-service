# Trocabook — Serviço de Analytics

Serviço de Analytics desenvolvido para o **Trocabook**, uma plataforma voltada à troca e venda de livros novos e usados.

O projeto é responsável pela aplicação de técnicas de **análise e mineração de dados** para extrair informações da plataforma e gerar indicadores, insights e projeções que auxiliem no acompanhamento da evolução do Trocabook e na tomada de decisões.

O serviço é desenvolvido em **Python** e utiliza **Pandas** para o processamento e análise dos dados. A disponibilização é realizada por meio de uma API REST desenvolvida em **FastAPI**, integrada ao sistema principal do Trocabook em **Spring Boot**.

---

## Objetivo

O objetivo do serviço é analisar dados relacionados aos usuários, anúncios e negociações do Trocabook, permitindo a geração de indicadores e projeções para apoiar o acompanhamento da plataforma e a tomada de decisões.

Inicialmente, o serviço contempla quatro frentes:

- Análise das negociações realizadas na plataforma;
- Análise dos anúncios publicados;
- Previsão da quantidade de novos usuários;
- Previsão da quantidade de novos anúncios.

As análises e os modelos foram inicialmente desenvolvidos e avaliados de forma experimental utilizando dados simulados. A utilização de dados reais da plataforma é realizada durante a integração com o sistema principal.

---

## Experimentos

O diretório `notebooks/` contém os experimentos utilizados para desenvolver e avaliar as abordagens iniciais do serviço de Analytics.

```text
notebooks/
├── experimento_analise_anuncios.ipynb
├── experimento_analise_negociacoes.ipynb
├── experimento_previsao_anuncios.ipynb
└── experimento_previsao_usuarios.ipynb
```

### Análise de negociações

O experimento de análise de negociações investiga o comportamento das negociações realizadas na plataforma.

Entre os aspectos analisados estão:

- Quantidade e distribuição das negociações;
- Comparação entre modalidades de negociação;
- Análise por categorias;
- Afinidade entre categorias em negociações de troca;
- Evolução temporal das negociações;
- Análise do tempo médio de finalização;
- Estimativas das taxas de finalização;
- Geração de insights a partir dos resultados.

Parte dessas análises está implementada no módulo `app/analytics/negociacao_analytics.py`.

### Análise de anúncios

O experimento de análise de anúncios investiga o comportamento das publicações realizadas na plataforma.

Entre os aspectos analisados estão:

- Quantidade de anúncios;
- Distribuição por tipo de negociação;
- Autores e categorias mais anunciados;
- Relação entre categorias e modalidades de negociação;
- Evolução mensal da quantidade de anúncios;
- Variações no volume de anúncios ao longo do tempo;
- Geração de insights a partir dos resultados.

A implementação reutilizável está disponível em `app/analytics/anuncio_analytics.py`, por meio da classe `AnuncioAnalytics`.

O módulo recebe os anúncios e realiza o processamento utilizando Pandas, retornando estruturas com indicadores gerais, distribuições, análises temporais e insights.

### Previsão de novos usuários

O experimento de previsão de usuários utiliza o histórico mensal de criação de usuários para estimar a quantidade de novos usuários em períodos futuros.

A implementação reutilizável está disponível em `app/analytics/previsao_temporal_analytics.py`, por meio da classe `PrevisaoTemporalAnalytics`.

O módulo prepara e valida a série temporal, completa meses sem registros com zero, avalia uma regressão linear utilizando os períodos finais como conjunto de teste e calcula as métricas MAE e RMSE. Depois, treina o modelo com todo o histórico disponível e gera projeções para os meses futuros.

O experimento contempla:

- Construção da série temporal mensal;
- Análise da evolução histórica;
- Utilização de um baseline de persistência;
- Utilização experimental de Regressão Linear;
- Avaliação utilizando MAE e RMSE;
- Projeções para horizontes de 1, 3, 6 e 12 meses.

### Previsão de novos anúncios

O experimento de previsão de anúncios utiliza o histórico mensal de criação de anúncios para estimar a quantidade de novos anúncios que poderão ser publicados em períodos futuros.

A previsão utiliza a mesma classe `PrevisaoTemporalAnalytics`, informando a coluna correspondente à quantidade de novos anúncios. Dessa forma, usuários e anúncios compartilham a implementação do modelo, alterando apenas a série mensal de entrada.

O experimento contempla:

- Construção da série temporal mensal;
- Análise da evolução histórica;
- Utilização de um baseline de persistência;
- Utilização experimental de Regressão Linear;
- Avaliação utilizando MAE e RMSE;
- Projeções para horizontes de 1, 3, 6 e 12 meses.

Os modelos preditivos utilizados nos experimentos representam abordagens iniciais e deverão ser reavaliados com os dados reais da plataforma antes de sua utilização integrada ao sistema principal.

---

## Camada de Serviço e API REST

A coordenação entre as análises descritivas, diagnósticas e preditivas é realizada pela classe **`TrocabookAnalyticsService`**, localizada em `app/services`.

A API expõe três endpoints principais via FastAPI em `app/controllers/analytics_controller.py`:

- **`POST /analytics/anuncios`**: Indicadores completos dos anúncios e previsão temporal de novos anúncios;
- **`POST /analytics/negociacoes`**: Indicadores detalhados, diagnósticos e afinidades das negociações;
- **`POST /analytics/previsao-temporal`**: Projeções temporais de novos cadastros de usuários.

---

## Estrutura do Projeto

A estrutura atual do serviço está organizada da seguinte forma:

```text
trocabook-analytics-service/
│
├── app/
│   ├── adapters/
│   │   ├── __init__.py
│   │   ├── anuncio_adapter.py
│   │   ├── negociacao_adapter.py
│   │   └── previsao_temporal_adapter.py
│   │
│   ├── analytics/
│   │   ├── __init__.py
│   │   ├── anuncio_analytics.py
│   │   ├── negociacao_analytics.py
│   │   └── previsao_temporal_analytics.py
│   │
│   ├── controllers/
│   │   ├── requests/
│   │   │   ├── __init__.py
│   │   │   ├── anuncio_request.py
│   │   │   ├── negociacao_request.py
│   │   │   └── previsao_usuarios_request.py
│   │   │
│   │   ├── responses/
│   │   │   ├── __init__.py
│   │   │   ├── anuncio_response.py
│   │   │   ├── negociacao_response.py
│   │   │   └── previsao_temporal_response.py
│   │   │
│   │   ├── __init__.py
│   │   └── analytics_controller.py
│   │
│   ├── enums/
│   │   ├── __init__.py
│   │   ├── status_negociacao.py
│   │   └── tipo_negociacao.py
│   │
│   ├── exceptions/
│   │   ├── __init__.py
│   │   └── analytics_exception.py
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   ├── anuncio.py
│   │   ├── negociacao.py
│   │   └── usuario.py
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   └── trocabook_analytics_service.py
│   │
│   ├── __init__.py
│   └── main.py
│
├── notebooks/
│   ├── experimento_analise_anuncios.ipynb
│   ├── experimento_analise_negociacoes.ipynb
│   ├── experimento_previsao_anuncios.ipynb
│   └── experimento_previsao_usuarios.ipynb
│
├── tests/
│   ├── __init__.py
│   ├── test_analytics_controller.py
│   ├── test_anuncio_analytics.py
│   ├── test_negociacao_analytics.py
│   ├── test_previsao_temporal_analytics.py
│   └── test_trocabook_analytics_service.py
│
├── .gitignore
├── requirements.txt
├── test_main.http
└── README.md
```

### Responsabilidades dos diretórios e arquivos

- `adapters/` — contém as classes adaptadoras que transformam DataFrames e estruturas internas em objetos DTO de resposta da API;
- `analytics/` — contém os módulos responsáveis pelo processamento, análise descritiva/diagnóstica e previsão temporal;
- `controllers/` — contém o controlador REST (`analytics_controller.py`), contratos de entrada (`requests/`) e respostas formatadas (`responses/`);
- `enums/` — contém as enumerações padronizadas de domínio, como tipos e status de negociação;
- `exceptions/` — contém as exceções customizadas da aplicação (`AnalyticsException`);
- `models/` — contém os modelos Pydantic de validação das entidades de domínio (`Anuncio`, `Negociacao`, `Usuario`);
- `services/` — contém o orquestrador `TrocabookAnalyticsService`;
- `notebooks/` — reúne os experimentos e protótipos de dados;
- `tests/` — contém a suíte completa de testes unitários e de integração com `TestClient`;
- `main.py` — ponto de entrada da aplicação FastAPI e registrador de exception handlers.

---

## Testes Automatizados

O serviço utiliza **pytest** e **pytest-cov** para testes automatizados e análise de cobertura de código.

Na execução mais recente, **98 testes foram aprovados**, alcançando **97% de cobertura geral** do projeto (com 100% de cobertura nos Controllers, Schemas e Entrypoint).

### Cobertura da suíte de testes (98 testes aprovados)

1. **Testes de análise de negociações (`tests/test_negociacao_analytics.py`) — 40 testes:**
   - Análise geral, distribuição por modalidade e por categorias;
   - Afinidade de categorias e combinações em trocas;
   - Tempo de finalização e ajuste estatístico Beta-Binomial;
   - Insights e resiliência a dados ausentes.

2. **Testes de análise de anúncios (`tests/test_anuncio_analytics.py`) — 16 testes:**
   - Indicadores gerais, distribuições por tipo, autor e categoria;
   - Análise temporal mensal, variação percentual e evolução por tipo;
   - Tratamento de registros nulos, datas inválidas e estruturas vazias.

3. **Testes de previsão temporal (`tests/test_previsao_temporal_analytics.py`) — 24 testes:**
   - Validação de séries mensais e preenchimento de lacunas temporais;
   - Cálculo de métricas de erro (MAE e RMSE);
   - Regras de histórico mínimo, projeções não negativas e validações.

4. **Testes do serviço orquestrador (`tests/test_trocabook_analytics_service.py`) — 9 testes:**
   - Inicialização e injeção de mocks;
   - Execução isolada dos métodos de anúncios, negociações e usuários;
   - Tratamento de séries temporais vazias ou insuficientes.

5. **Testes de integração do Controller (`tests/test_analytics_controller.py`) — 9 testes:**
   - Requisições HTTP via FastAPI `TestClient`;
   - Validação de payload correto e retorno 200 OK;
   - Validação de parâmetros inválidos com HTTP 422;
   - Manipulação de erro interno e captura da `AnalyticsException` com HTTP 500.

### Execução dos testes

Para executar a suíte completa de testes:

```bash
pytest -v
```

Para executar os testes com relatório detalhado de cobertura:

```bash
pytest --cov=app --cov-report=term-missing
```

---

## Integração com o Trocabook

O serviço de Analytics é integrado ao sistema principal do Trocabook por meio de uma API REST.

O sistema principal, desenvolvido em **Spring Boot**, é responsável pela persistência e recuperação dos dados da aplicação.

A comunicação entre os sistemas segue o fluxo abaixo:

```text
Trocabook
(Spring Boot)
     │
     │ DTOs / REST HTTP POST
     ▼
Serviço de Analytics
(FastAPI)
     │
     ▼
AnalyticsController
     │
     ▼
TrocabookAnalyticsService
     │
     ├── AnuncioAnalytics
     ├── NegociacaoAnalytics
     └── PrevisaoTemporalAnalytics
     │
     ▼
Adapters (AnuncioAdapter, NegociacaoAdapter, PrevisaoTemporalAdapter)
     │
     ▼
Respostas JSON Formatadas
     │
     ▼
Trocabook
(Spring Boot)
     │
     ▼
Dashboard administrativo
```

O serviço de Analytics não acessa diretamente o banco de dados. O sistema principal recupera os dados necessários e os envia em payloads JSON para cada endpoint correspondente.

---

## Tecnologias

- **Python** — linguagem de programação principal;
- **FastAPI** — framework para disponibilização da API REST;
- **Pandas** — manipulação e análise de dados;
- **NumPy** — operações numéricas;
- **Scikit-learn** — modelos de regressão e métricas de avaliação;
- **SciPy** — otimização por máxima verossimilhança (ajuste Beta-Binomial);
- **Pydantic** — validação de dados e contratos de DTO;
- **Uvicorn** — servidor ASGI para execução da API;
- **Pytest & Pytest-cov** — suíte de testes e medição de cobertura;
- **Jupyter Notebook** — ambiente experimental.
- **HTTPX2** — para suporte aos testes da API com `TestClient`.

---

## Executando o Projeto

### 1. Clone o repositório

```bash
git clone https://github.com/PedroAmaralMa/trocabook-analytics-service.git
```

Entre no diretório:

```bash
cd trocabook-analytics-service
```

### 2. Crie um ambiente virtual

```bash
python -m venv .venv
```

### 3. Ative o ambiente virtual

**Windows:**

```bash
.venv\Scripts\activate
```

**Linux/macOS:**

```bash
source .venv/bin/activate
```

### 4. Instale as dependências

```bash
pip install -r requirements.txt
```

### 5. Execute os testes

```bash
pytest -v
```

Para verificar a cobertura de código:

```bash
pytest --cov=app --cov-report=term-missing
```

### 6. Execute a API

```bash
python -m uvicorn app.main:app --reload --port=8001
```

A documentação interativa da API estará disponível em:
- Swagger UI: `http://127.0.0.1:8001/docs`
- ReDoc: `http://127.0.0.1:8001/redoc`

---

## Status

**Pronto para integração.**

### Concluído

- [x] Criação da estrutura inicial do serviço;
- [x] Desenvolvimento dos experimentos em Jupyter Notebooks;
- [x] Definição dos modelos Pydantic de domínio (`Anuncio`, `Negociacao`, `Usuario`);
- [x] Implementação dos módulos de análise (`AnuncioAnalytics`, `NegociacaoAnalytics`, `PrevisaoTemporalAnalytics`);
- [x] Implementação do orquestrador `TrocabookAnalyticsService`;
- [x] Implementação dos modelos Pydantic de requisição e resposta (Requests/Responses DTOs);
- [x] Implementação dos adaptadores de dados (`AnuncioAdapter`, `NegociacaoAdapter`, `PrevisaoTemporalAdapter`);
- [x] Implementação do controlador REST FastAPI (`AnalyticsController`) com três endpoints;
- [x] Tratamento de exceção padronizado com `AnalyticsException` e HTTP 500;
- [x] Suíte completa de 98 testes automatizados aprovados com 97% de cobertura geral.
- [x] Integração do cliente HTTP no sistema principal do Trocabook (Spring Boot);
- [x] Renderização dos dados consumidos no dashboard administrativo da plataforma;

### Próximas etapas


- [ ] Validação dos modelos preditivos com volume maior de dados.

---

## Projeto Trocabook

O Trocabook é um projeto acadêmico desenvolvido com o objetivo de incentivar a reutilização de livros por meio de uma plataforma que possibilita a troca e venda de livros novos e usados.

O projeto está relacionado ao **Objetivo de Desenvolvimento Sustentável 12 (ODS 12) — Consumo e Produção Responsáveis**, especialmente no que diz respeito ao consumo consciente e à redução do desperdício por meio da reutilização de recursos.
