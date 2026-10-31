# Trocabook — Serviço de Analytics

Serviço de Analytics desenvolvido para o **Trocabook**, uma plataforma voltada à troca e venda de livros novos e usados.

O projeto é responsável pela aplicação de técnicas de **análise e mineração de dados** para extrair informações da plataforma e gerar indicadores, insights e projeções que auxiliem no acompanhamento da evolução do Trocabook e na tomada de decisões.

O serviço é desenvolvido em **Python** e utiliza **Pandas** para o processamento e análise dos dados. A disponibilização por meio de uma API REST utilizando **FastAPI** está prevista para permitir sua integração com o sistema principal do Trocabook, desenvolvido em **Spring Boot**.

---

## Objetivo

O objetivo do serviço é analisar dados relacionados aos usuários, anúncios e negociações do Trocabook, permitindo a geração de indicadores e projeções para apoiar o acompanhamento da plataforma e a tomada de decisões.

Inicialmente, o serviço contempla quatro frentes:

- Análise das negociações realizadas na plataforma;
- Análise dos anúncios publicados;
- Previsão da quantidade de novos usuários;
- Previsão da quantidade de novos anúncios.

As análises e os modelos foram inicialmente desenvolvidos e avaliados de forma experimental utilizando dados simulados. A utilização de dados reais da plataforma será realizada durante a integração com o sistema principal.

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

## Camada de Serviço (Orquestração)

A coordenação entre as diferentes análises descritivas, diagnósticas e preditivas é realizada pela classe **`TrocabookAnalyticsService`**, localizada em `app/service/trocabook_analytics_service.py`.

### Responsabilidades do Serviço:

- **Receber os dados de domínio:** aceita listas de objetos ou dicionários de `Anuncio`, `Negociacao` e `Usuario`;
- **Delegar o processamento:** aciona `AnuncioAnalytics` e `NegociacaoAnalytics` para calcular estatísticas e métricas de desempenho;
- **Executar as projeções temporais:** extrai automaticamente as séries mensais necessárias e aciona `PrevisaoTemporalAnalytics` para gerar previsões futuras de anúncios e usuários;
- **Consolidar insights:** unifica e padroniza as interpretações geradas pelos módulos em um relatório estruturado único.

---

## Estrutura do Projeto

A estrutura atual do serviço está organizada da seguinte forma:

```text
trocabook-analytics-service/
│
├── app/
│   ├── analytics/
│   │   ├── __init__.py
│   │   ├── anuncio_analytics.py
│   │   ├── negociacao_analytics.py
│   │   └── previsao_temporal_analytics.py
│   │
│   ├── enums/
│   │   ├── __init__.py
│   │   ├── status_negociacao.py
│   │   └── tipo_negociacao.py
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   ├── anuncio.py
│   │   ├── negociacao.py
│   │   └── usuario.py
│   │
│   ├── service/
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

- `analytics/` — contém os módulos responsáveis pelo processamento, análise e geração de indicadores, insights e previsões temporais;
- `enums/` — contém as enumerações utilizadas para representar valores padronizados, como tipos e status de negociação;
- `models/` — contém os modelos Pydantic para estruturação e validação dos dados;
- `service/` — contém a camada de orquestração responsável por coordenar a execução de todas as análises e consolidar os resultados;
- `notebooks/` — reúne os experimentos de análise de dados e desenvolvimento dos modelos preditivos;
- `tests/` — contém os testes automatizados para verificar os comportamentos esperados de todos os módulos;
- `main.py` — ponto de entrada da aplicação FastAPI.

---

## Testes Automatizados

O serviço utiliza **pytest** e **pytest-cov** para a implementação de testes automatizados e análise de cobertura de código.

Na última execução registrada, todos os **88 testes foram aprovados**, alcançando **100% de cobertura** na camada de serviço.

### Cobertura da suíte de testes (88 testes aprovados)

1. **Testes de análise de negociações (`tests/test_negociacao_analytics.py`) — 40 testes:**
   - Análise geral, distribuição por modalidade e por categorias;
   - Afinidade de categorias e combinações entre anúncios em trocas;
   - Análise do tempo de finalização e ajuste estatístico Beta-Binomial;
   - Geração de insights e tratamento de dados ausentes ou inconsistentes.

2. **Testes de análise de anúncios (`tests/test_anuncio_analytics.py`) — 16 testes:**
   - Indicadores gerais, distribuições por tipo, autor e categoria;
   - Análise temporal mensal, variação percentual e evolução por tipo;
   - Tratamento de registros nulos, datas inválidas e estruturas vazias.

3. **Testes de previsão temporal (`tests/test_previsao_temporal_analytics.py`) — 24 testes:**
   - Validação de séries mensais e preenchimento de períodos ausentes;
   - Cálculo das métricas de erro (MAE e RMSE) em conjunto de validação;
   - Regras de histórico mínimo, projeções não negativas e validação de tipos de dados.

4. **Testes do serviço orquestrador (`tests/test_trocabook_analytics_service.py`) — 8 testes:**
   - Inicialização com dependências padrão e injeção de mocks;
   - Validação da estrutura unificada do relatório consolidado;
   - Formatação e rotulagem correta das origens dos insights;
   - Tratamento de séries vazias, chaves ausentes e histórico insuficiente de usuários.

### Execução dos testes

Para executar todos os testes do serviço:

```bash
pytest -v
```

Para executar os testes com a análise detalhada de cobertura de código:

```bash
pytest --cov=app/service --cov-report=term-missing
```

---

## Integração com o Trocabook

O serviço de Analytics será integrado ao sistema principal do Trocabook por meio de uma API REST.

O sistema principal, desenvolvido em **Spring Boot**, permanecerá responsável pela persistência e recuperação dos dados da aplicação.

A comunicação prevista entre os sistemas seguirá o fluxo conceitual abaixo:

```text
Trocabook
(Spring Boot)
     │
     │ DTOs / REST
     ▼
Serviço de Analytics
(FastAPI)
     │
     ▼
TrocabookAnalyticsService
     │
     ├── AnuncioAnalytics
     ├── NegociacaoAnalytics
     └── PrevisaoTemporalAnalytics
     │
     ▼
Relatório Consolidado (Indicadores e Projeções)
     │
     ▼
Trocabook
(Spring Boot)
     │
     ▼
Dashboard administrativo
```

O serviço de Analytics não acessará diretamente o **Firebase**. O sistema principal será responsável por recuperar os dados necessários e enviá-los ao serviço por meio de DTOs específicos para cada análise.

Essa separação mantém a responsabilidade pela persistência no sistema principal e permite que o serviço de Analytics permaneça focado no processamento, na análise e na geração de indicadores e projeções.

---

## Tecnologias

O projeto utiliza ou prevê a utilização das seguintes tecnologias e bibliotecas:

- **Python** — linguagem de programação do serviço;
- **FastAPI** — framework para disponibilização da API REST;
- **Pandas** — manipulação e análise de dados;
- **NumPy** — operações numéricas;
- **Scikit-learn** — modelos de regressão e métricas de avaliação;
- **SciPy** — otimização por máxima verossimilhança (ajuste Beta-Binomial);
- **Matplotlib** — visualização de dados nos experimentos;
- **Pydantic** — validação e estruturação de dados;
- **Jupyter Notebook** — ambiente para experimentação;
- **Uvicorn** — servidor ASGI para execução da aplicação FastAPI;
- **Pytest** — implementação dos testes automatizados;
- **Pytest-cov** — análise da cobertura dos testes.

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

Para executar os testes com cobertura:

```bash
pytest --cov=app/service --cov-report=term-missing
```

### 6. Execute a API

```bash
python -m uvicorn app.main:app --reload
```

---

## Status

**Em desenvolvimento.**

### Concluído

- [x] Criação da estrutura inicial do serviço;
- [x] Desenvolvimento do experimento de análise de negociações;
- [x] Desenvolvimento do experimento de análise de anúncios;
- [x] Desenvolvimento do experimento de previsão de novos usuários;
- [x] Desenvolvimento do experimento de previsão de novos anúncios;
- [x] Definição inicial dos modelos Pydantic utilizados pelo serviço;
- [x] Implementação inicial das análises de negociações;
- [x] Implementação dos testes automatizados para as análises de negociações;
- [x] Implementação inicial do módulo reutilizável de previsão temporal;
- [x] Criação dos testes automatizados para `PrevisaoTemporalAnalytics`;
- [x] Implementação inicial do módulo de análise de anúncios;
- [x] Criação dos testes automatizados para `AnuncioAnalytics`;
- [x] Implementação da camada de serviço (`TrocabookAnalyticsService`) para coordenação dos módulos de analytics e previsão;
- [x] Criação dos testes automatizados para a camada de serviço (`TrocabookAnalyticsService`) com 100% de cobertura;

### Próximas etapas

- [ ] Implementação do controller / router FastAPI (`AnalyticsController`);
- [ ] Implementação das funções de serialização/mapeamento de respostas;
- [ ] Implementação dos schemas de validação de requisição (`AnalyticsRelatorioRequest`);
- [ ] Integração e validação dos endpoints REST;
- [ ] Integração com o sistema principal do Trocabook (Spring Boot);
- [ ] Integração dos resultados ao dashboard administrativo;
- [ ] Validação das análises e previsões com dados reais da plataforma.

---

## Projeto Trocabook

O Trocabook é um projeto acadêmico desenvolvido com o objetivo de incentivar a reutilização de livros por meio de uma plataforma que possibilita a troca e venda de livros novos e usados.

O projeto está relacionado ao **Objetivo de Desenvolvimento Sustentável 12 (ODS 12) — Consumo e Produção Responsáveis**, especialmente no que diz respeito ao consumo consciente e à redução do desperdício por meio da reutilização de recursos.