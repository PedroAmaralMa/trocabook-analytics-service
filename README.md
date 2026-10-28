# Trocabook — Serviço de Analytics

Serviço de analytics desenvolvido para o **Trocabook**, uma plataforma voltada à troca e venda de livros usados.

Este projeto é responsável pela aplicação de técnicas de **análise e mineração de dados** para extrair informações dos dados da plataforma e gerar projeções que auxiliem no acompanhamento da evolução do Trocabook.

O serviço é desenvolvido em **Python** e utilizará uma API REST com **FastAPI** para integração com o sistema principal do Trocabook desenvolvido em **Spring Boot**.

---

## Objetivo

O objetivo do serviço é analisar dados relacionados aos usuários, anúncios e negociações do Trocabook, permitindo a geração de indicadores e projeções para apoio ao acompanhamento da plataforma.

Inicialmente, o serviço contempla quatro frentes:

- análise das negociações realizadas na plataforma;
- análise dos anúncios publicados;
- previsão da quantidade de novos usuários;
- previsão da quantidade de novos anúncios.

As análises e modelos foram inicialmente desenvolvidos e avaliados de forma experimental utilizando dados simulados. A utilização de dados reais da plataforma será realizada durante a integração do serviço com o sistema principal.

---

## Experimentos

O diretório `notebooks/` contém os experimentos utilizados para desenvolver e validar as abordagens iniciais do serviço de Analytics.

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

- quantidade e distribuição das negociações;
- comparação entre modalidades de negociação;
- análise por categorias;
- afinidade entre categorias em negociações de troca;
- evolução temporal das negociações;
- confiabilidade das taxas observadas;
- geração de insights a partir dos resultados.

### Análise de anúncios

O experimento de análise de anúncios investiga o comportamento das publicações realizadas na plataforma.

Entre os aspectos analisados estão:

- quantidade de anúncios;
- distribuição por tipo de negociação;
- categorias mais anunciadas;
- relação entre categorias e modalidades de negociação;
- evolução mensal da quantidade de anúncios;
- variações no volume de anúncios ao longo do tempo.

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

Os modelos preditivos utilizados nos experimentos representam abordagens iniciais e deverão ser reavaliados com os dados reais da plataforma.

---

## Estrutura do Projeto

A estrutura será expandida conforme as funcionalidades do serviço forem implementadas.

```text
trocabook-analytics-service/
│
├── app/
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
├── .gitignore
├── requirements.txt
├── test_main.http
└── README.md
```

### Responsabilidades atuais

- `enums/` — enumerações utilizadas pelos modelos do serviço;
- `models/` — modelos utilizados para representar os dados recebidos pelo serviço;
- `notebooks/` — experimentos de análise de dados e desenvolvimento dos modelos preditivos;
- `main.py` — ponto de entrada da aplicação FastAPI.

Novas camadas serão adicionadas conforme a implementação do serviço evoluir.

---

## Integração com o Trocabook

O serviço de Analytics será integrado ao sistema principal do Trocabook através de uma API REST.

O sistema principal, desenvolvido em **Spring Boot**, permanece responsável pela persistência e recuperação dos dados da aplicação.

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

Essa separação mantém a responsabilidade pela persistência no sistema principal e permite que o serviço de Analytics permaneça focado no processamento, análise e geração de projeções.

---

## Tecnologias

O projeto utiliza:

- Python;
- FastAPI;
- Pandas;
- NumPy;
- Scikit-learn;
- SciPy;
- Matplotlib;
- Pydantic;
- Jupyter Notebook;
- Uvicorn.

---

## Status

**Em desenvolvimento.**

Até o momento:

- [x] Criação da estrutura inicial do serviço;
- [x] Experimento de análise de negociações;
- [x] Experimento de análise de anúncios;
- [x] Experimento de previsão de novos usuários;
- [x] Experimento de previsão de novos anúncios;
- [x] Definição inicial dos modelos utilizados pelo serviço;
- [ ] Implementação das análises no serviço;
- [ ] Implementação dos modelos preditivos no serviço;
- [ ] Implementação dos adapters;
- [ ] Implementação dos contratos de Request e Response;
- [ ] Implementação dos services;
- [ ] Implementação dos endpoints REST;
- [ ] Integração com o sistema principal do Trocabook;
- [ ] Integração dos resultados ao Dashboard administrativo;
- [ ] Implementação dos testes automatizados;
- [ ] Validação das análises e previsões com dados reais.

---

## Projeto Trocabook

O Trocabook é um projeto acadêmico desenvolvido com o objetivo de incentivar a reutilização de livros por meio de uma plataforma que possibilita a troca e venda de livros usados.

O projeto está relacionado ao **Objetivo de Desenvolvimento Sustentável 12 (ODS 12) — Consumo e Produção Responsáveis**.