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
│   └── test_previsao_temporal_analytics.py
│
├── .gitignore
├── requirements.txt
├── test_main.http
└── README.md
```

### Responsabilidades dos diretórios e arquivos

- `analytics/` — contém os módulos responsáveis pelo processamento, análise e geração de indicadores, insights e previsões temporais;
- `enums/` — contém as enumerações utilizadas para representar valores padronizados, como tipos e status de negociação;
- `models/` — contém os modelos utilizados para representar e estruturar os dados recebidos pelo serviço;
- `notebooks/` — reúne os experimentos de análise de dados e desenvolvimento dos modelos preditivos;
- `tests/` — contém os testes automatizados utilizados para verificar os comportamentos esperados dos módulos de análise e previsão;
- `main.py` — ponto de entrada da aplicação FastAPI.

A arquitetura poderá receber novas camadas, como adapters, services e controllers, conforme a implementação da API e a integração com o sistema principal evoluírem.
---

## Testes Automatizados

O serviço utiliza **pytest** para a implementação dos testes automatizados.

Os testes verificam os comportamentos esperados dos módulos de análise e previsão, incluindo cenários comuns, dados incompletos, entradas inválidas e situações em que não existem informações suficientes para determinadas operações.

### Testes de análise de negociações

O módulo `NegociacaoAnalytics` possui uma suíte de testes que contempla:

- Análise geral das negociações;
- Distribuição por modalidade;
- Análise por categorias;
- Afinidade entre categorias em negociações de troca;
- Evolução temporal das negociações;
- Análise do tempo médio de finalização;
- Estimativas das taxas de finalização;
- Geração de insights;
- Tratamento de dados ausentes e datas inválidas;
- Situações com informações insuficientes para determinadas estimativas.

Na execução anteriormente registrada, **40 testes foram aprovados**, sem falhas.

### Testes de análise de anúncios

O módulo `AnuncioAnalytics` possui testes automatizados em `tests/test_anuncio_analytics.py`.

Os testes verificam:

- Execução geral da análise dos anúncios;
- Cálculo dos indicadores gerais;
- Distribuição por tipo de negociação;
- Distribuição por autor;
- Distribuição por categoria;
- Relação entre categorias e tipos de negociação;
- Análise temporal dos anúncios;
- Resumo mensal;
- Quantidade de anúncios por mês e modalidade;
- Evolução mensal por tipo de negociação;
- Geração de insights;
- Retorno de estruturas vazias quando não existem anúncios;
- Tratamento de dados incompletos;
- Tratamento de entradas nulas;
- Normalização dos tipos de negociação, incluindo valores de Enum.

### Testes de previsão temporal

O módulo `PrevisaoTemporalAnalytics` possui testes automatizados em `tests/test_previsao_temporal_analytics.py`.

Os testes verificam:

- Estrutura do retorno;
- Utilização da mesma implementação para séries de usuários e anúncios;
- Preenchimento de meses ausentes;
- Validação dos dados de entrada;
- Histórico mínimo necessário;
- Geração de projeções não negativas.

A suíte específica de previsão temporal contém **11 casos de teste implementados**.

### Execução dos testes

Para executar todos os testes do serviço:

```bash
pytest -v
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
Análise e processamento
dos dados
     │
     ▼
Indicadores e projeções
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

O fluxo apresentado representa a arquitetura planejada para a integração. A comunicação completa entre os sistemas e a apresentação dos resultados no dashboard ainda dependem das respectivas implementações.

---

## Tecnologias

O projeto utiliza ou prevê a utilização das seguintes tecnologias e bibliotecas:

- **Python** — linguagem de programação do serviço;
- **FastAPI** — framework previsto para disponibilizar a API REST;
- **Pandas** — manipulação e análise de dados;
- **NumPy** — operações numéricas;
- **Scikit-learn** — experimentos com modelos de aprendizado de máquina e métricas de avaliação;
- **SciPy** — métodos de otimização e cálculos estatísticos;
- **Matplotlib** — visualização de dados nos experimentos;
- **Pydantic** — validação e estruturação de dados;
- **Jupyter Notebook** — ambiente para experimentação e análise;
- **Uvicorn** — servidor ASGI para execução da aplicação FastAPI;
- **Pytest** — implementação dos testes automatizados;
- **Pytest-cov** — análise da cobertura dos testes.

A utilização de cada tecnologia nas funcionalidades disponibilizadas pelo serviço depende da implementação correspondente.

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
pytest --cov=app --cov-report=term-missing
```

### 6. Execute a API

```bash
python -m uvicorn app.main:app --reload
```

A aplicação será iniciada localmente na porta configurada pelo projeto.

A disponibilização dos endpoints e a documentação automática do FastAPI dependerão da implementação das rotas correspondentes.

---

## Status

**Em desenvolvimento.**

### Concluído

- [x] Criação da estrutura inicial do serviço;
- [x] Desenvolvimento do experimento de análise de negociações;
- [x] Desenvolvimento do experimento de análise de anúncios;
- [x] Desenvolvimento do experimento de previsão de novos usuários;
- [x] Desenvolvimento do experimento de previsão de novos anúncios;
- [x] Definição inicial dos modelos utilizados pelo serviço;
- [x] Implementação inicial das análises de negociações;
- [x] Implementação dos testes automatizados para as análises de negociações;
- [x] Implementação inicial do módulo reutilizável de previsão temporal;
- [x] Criação dos testes automatizados para `PrevisaoTemporalAnalytics`;
- [x] Implementação inicial do módulo de análise de anúncios;
- [x] Criação dos testes automatizados para `AnuncioAnalytics`;

### Próximas etapas

- [ ] Implementação das demais análises no serviço;
- [ ] Implementação dos modelos preditivos no serviço;
- [ ] Implementação dos adapters;
- [ ] Implementação dos contratos de Request e Response;
- [ ] Implementação dos services;
- [ ] Implementação e validação dos endpoints REST;
- [ ] Integração com o sistema principal do Trocabook;
- [ ] Integração dos resultados ao dashboard administrativo;
- [ ] Ampliação dos testes automatizados para as demais funcionalidades;
- [ ] Validação das análises e previsões com dados reais.

---

## Projeto Trocabook

O Trocabook é um projeto acadêmico desenvolvido com o objetivo de incentivar a reutilização de livros por meio de uma plataforma que possibilita a troca e venda de livros novos e usados.

O projeto está relacionado ao **Objetivo de Desenvolvimento Sustentável 12 (ODS 12) — Consumo e Produção Responsáveis**, especialmente no que diz respeito ao consumo consciente e à redução do desperdício por meio da reutilização de recursos.