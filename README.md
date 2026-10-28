# Trocabook — Serviço de Analytics

Serviço de analytics desenvolvido para o **Trocabook**, uma plataforma voltada à troca e venda de livros novos e usados.

Este projeto é responsável pela aplicação de técnicas de **análise e mineração de dados** para extrair informações dos dados da plataforma e gerar indicadores, insights e projeções que auxiliem no acompanhamento da evolução do Trocabook.

O serviço é desenvolvido em **Python** e utiliza **FastAPI** como tecnologia prevista para a disponibilização de uma API REST, permitindo a integração com o sistema principal do Trocabook, desenvolvido em **Spring Boot**.

---

## Objetivo

O objetivo do serviço é analisar dados relacionados aos usuários, anúncios e negociações do Trocabook, permitindo a geração de indicadores e projeções para apoiar o acompanhamento da plataforma e a tomada de decisões.

Inicialmente, o serviço contempla quatro frentes:

- análise das negociações realizadas na plataforma;
- análise dos anúncios publicados;
- previsão da quantidade de novos usuários;
- previsão da quantidade de novos anúncios.

As análises e os modelos foram inicialmente desenvolvidos e avaliados de forma experimental utilizando dados simulados. A utilização de dados reais da plataforma será realizada durante a integração do serviço com o sistema principal.

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

O experimento de análise de negociações investiga o comportamento das negociações realizadas na plataforma. Parte dessas análises já foi implementada no módulo `app/analytics/negociacao_analytics.py`.

Entre os aspectos analisados estão:

- quantidade e distribuição das negociações;
- comparação entre modalidades de negociação;
- análise por categorias;
- afinidade entre categorias em negociações de troca;
- evolução temporal das negociações;
- análise do tempo médio de finalização;
- estimativas das taxas de finalização;
- geração de insights a partir dos resultados.

O módulo conta com testes automatizados para verificar os comportamentos esperados das análises, incluindo cenários com dados ausentes, datas inválidas, diferentes modalidades de negociação e condições com informações insuficientes para determinadas estimativas.

Na execução mais recente dos testes, **40 testes foram aprovados**, sem falhas. A cobertura anteriormente registrada para o módulo foi de **98%**.

Esses resultados se referem aos testes automatizados do módulo de análise de negociações e não representam uma validação completa de todo o serviço ou de sua integração com o sistema principal.

### Análise de anúncios

O experimento de análise de anúncios investiga o comportamento das publicações realizadas na plataforma.

Entre os aspectos analisados estão:

- quantidade de anúncios;
- distribuição por tipo de negociação;
- categorias mais anunciadas;
- relação entre categorias e modalidades de negociação;
- evolução mensal da quantidade de anúncios;
- variações no volume de anúncios ao longo do tempo.

A disponibilização dessa análise por meio da API do serviço permanece condicionada à implementação e à integração correspondentes.

### Previsão de novos usuários

O experimento de previsão de usuários utiliza o histórico mensal de criação de usuários para estimar a quantidade de novos usuários em períodos futuros.

O experimento contempla:

- construção da série temporal mensal;
- análise da evolução histórica;
- utilização de um baseline de persistência;
- utilização experimental de Regressão Linear;
- avaliação utilizando MAE e RMSE;
- projeções para horizontes de 1, 3, 6 e 12 meses.

### Previsão de novos anúncios

O experimento de previsão de anúncios utiliza o histórico mensal de criação de anúncios para estimar a quantidade de novos anúncios que poderão ser publicados em períodos futuros.

O experimento contempla:

- construção da série temporal mensal;
- análise da evolução histórica;
- utilização de um baseline de persistência;
- utilização experimental de Regressão Linear;
- avaliação utilizando MAE e RMSE;
- projeções para horizontes de 1, 3, 6 e 12 meses.

Os modelos preditivos utilizados nos experimentos representam abordagens iniciais e deverão ser reavaliados com os dados reais da plataforma antes de sua utilização integrada ao sistema principal.

---

## Estrutura do Projeto

A estrutura abaixo representa os principais diretórios e arquivos relacionados ao serviço. Ela deverá ser ajustada conforme novas funcionalidades e camadas forem implementadas.

```text
trocabook-analytics-service/
│
├── app/
│   ├── analytics/
│   │   └── negociacao_analytics.py
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
│   └── test_negociacao_analytics.py
│
├── .gitignore
├── requirements.txt
├── test_main.http
└── README.md
```

### Responsabilidades dos diretórios e arquivos

- `analytics/` — contém os módulos responsáveis pelo processamento, análise e geração de indicadores e insights dos dados da plataforma;
- `enums/` — contém as enumerações utilizadas pelos modelos do serviço;
- `models/` — contém os modelos utilizados para representar os dados recebidos pelo serviço;
- `notebooks/` — reúne os experimentos de análise de dados e desenvolvimento dos modelos preditivos;
- `tests/` — contém os testes automatizados utilizados para verificar os comportamentos esperados das funcionalidades implementadas;
- `main.py` — ponto de entrada da aplicação FastAPI.

Novas camadas, como adapters, services e contratos específicos de requisição e resposta, serão adicionadas conforme a arquitetura do serviço evoluir.

---

## Testes Automatizados

Os testes automatizados verificam o comportamento das funcionalidades implementadas, ajudando a identificar falhas e a preservar os resultados esperados durante futuras alterações no código.

Atualmente, o módulo de análise de negociações possui uma suíte de testes que contempla cenários comuns, dados ausentes, datas inválidas, diferentes tipos de negociação e situações em que não existem informações suficientes para produzir determinadas análises.

Na execução mais recente:

- **40 testes aprovados**;
- **0 testes com falha**;
- tempo de execução de aproximadamente 5,25 segundos;
- cobertura anteriormente registrada de 98% para `app/analytics/negociacao_analytics.py`.

Para executar os testes, utilize:

```bash
pytest
```

Para executar os testes com relatório de cobertura do módulo de análise de negociações:

```bash
pytest --cov=app.analytics.negociacao_analytics --cov-report=term-missing
```

A cobertura deve ser interpretada considerando o módulo especificado no comando. Os resultados apresentados não representam necessariamente a cobertura total da aplicação.

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
- **Uvicorn** — servidor ASGI para execução da aplicação FastAPI.

A utilização de cada tecnologia nas funcionalidades disponibilizadas pelo serviço depende da implementação correspondente.

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
- [x] Execução da suíte de testes de negociações, com 40 testes aprovados.

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

O projeto está relacionado ao **Objetivo de Desenvolvimento Sustentável 12 (ODS 12) — Consumo e Produção Responsáveis**, especialmente no que diz respeito