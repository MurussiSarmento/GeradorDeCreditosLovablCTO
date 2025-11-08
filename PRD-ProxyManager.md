# Product Requirements Document (PRD)
## Proxy Manager & Validator Tool

**Version:** 1.0  
**Date:** November 7, 2025  
**Document Owner:** Product Development Team  
**Status:** Draft

---

## 1. Executive Summary

### 1.1 Product Overview
Proxy Manager & Validator é uma aplicação desktop Python com interface gráfica moderna que permite aos usuários buscar, validar e gerenciar proxies através de múltiplas fontes. A ferramenta oferece funcionalidades de scraping de proxies (aleatórios ou filtrados por país), validação contra URLs customizáveis, e uma API REST para integração com outras aplicações.

### 1.2 Problem Statement
Usuários que trabalham com web scraping, automação, testes de segurança e operações que requerem múltiplos IPs enfrentam dificuldades para:
- Encontrar proxies válidos e funcionais de forma rápida
- Validar grandes listas de proxies manualmente
- Filtrar proxies por localização geográfica
- Integrar funcionalidades de proxy em suas aplicações existentes
- Garantir que proxies funcionem em sites específicos

### 1.3 Objectives
- Automatizar o processo de descoberta e validação de proxies
- Fornecer interface intuitiva para usuários não-técnicos
- Permitir validação em tempo real contra URLs customizadas
- Oferecer API REST para integração programática
- Suportar diferentes protocolos de proxy (HTTP, HTTPS, SOCKS4, SOCKS5)

### 1.4 Success Metrics
- **Performance:** Validar 100+ proxies em menos de 2 minutos
- **Acurácia:** Taxa de detecção de proxies funcionais > 95%
- **Usabilidade:** Tempo médio de aprendizado < 5 minutos
- **API:** Tempo de resposta < 500ms para endpoints básicos
- **Confiabilidade:** Uptime da aplicação > 99%

---

## 2. Stakeholders

| Stakeholder | Role | Involvement |
|------------|------|-------------|
| Desenvolvedores | Usuários Primários | Uso diário para scraping/automação |
| QA Engineers | Usuários Secundários | Testes de aplicações web |
| DevOps | Usuários Terciários | Rotação de IPs em infraestrutura |
| Security Researchers | Usuários Especializados | Pentesting e análise de segurança |

---

## 3. Product Features & Requirements

### 3.1 PARTE 1: Proxy Scraper com UI

#### 3.1.1 Interface Gráfica (GUI)
**Prioridade:** Alta  
**Framework:** CustomTkinter

**Requisitos Funcionais:**
- **FR-1.1.1:** Interface moderna com tema dark/light mode
- **FR-1.1.2:** Tela principal dividida em três seções:
  - Seção de configuração (filtros e opções)
  - Seção de resultados (tabela com proxies)
  - Seção de logs (status das operações)
- **FR-1.1.3:** Menu superior com opções: File, Tools, Settings, Help
- **FR-1.1.4:** Barra de status na parte inferior mostrando: total de proxies, proxies válidos, operação em andamento

**Requisitos Não-Funcionais:**
- **NFR-1.1.1:** Interface responsiva (sem freeze durante operações)
- **NFR-1.1.2:** Suporte a resoluções mínimas de 1280x720
- **NFR-1.1.3:** Tempo de inicialização < 3 segundos

#### 3.1.2 Funcionalidade de Scraping
**Prioridade:** Alta

**Requisitos Funcionais:**
- **FR-1.2.1:** Botão "Random Proxies" para buscar proxies aleatórios
- **FR-1.2.2:** Dropdown "Filter by Country" com lista de países (mínimo 20 países principais)
- **FR-1.2.3:** Campo numérico "Quantity" para definir quantidade de proxies (1-1000)
- **FR-1.2.4:** Checkbox para selecionar protocolos: HTTP, HTTPS, SOCKS4, SOCKS5
- **FR-1.2.5:** Botão "Start Scraping" para iniciar a busca
- **FR-1.2.6:** Botão "Stop" para cancelar operação em andamento
- **FR-1.2.7:** Barra de progresso mostrando status da operação

**Fontes de Proxies (integrar pelo menos 5):**
- ProxyScrape API
- Free-proxy-list.net
- SSLProxies.org
- GatherProxy
- Spys.one
- PubProxy
- Proxify

**Requisitos Não-Funcionais:**
- **NFR-1.2.1:** Scraping em background usando threading/asyncio
- **NFR-1.2.2:** Timeout máximo de 30 segundos por fonte
- **NFR-1.2.3:** Deduplicação automática de proxies

**Requisitos Técnicos:**
- **TR-1.2.1:** Usar `aiohttp` para requisições assíncronas
- **TR-1.2.2:** Implementar rate limiting para evitar bloqueios
- **TR-1.2.3:** Parser HTML com `BeautifulSoup4` ou `lxml`
- **TR-1.2.4:** Armazenar proxies temporariamente em estrutura de dados eficiente

#### 3.1.3 Tabela de Resultados
**Prioridade:** Alta

**Requisitos Funcionais:**
- **FR-1.3.1:** Colunas da tabela: IP:Port, Protocol, Country, Anonymity, Speed (ms), Status
- **FR-1.3.2:** Sorting por qualquer coluna
- **FR-1.3.3:** Filtros inline para buscar proxies específicos
- **FR-1.3.4:** Seleção múltipla de proxies (Ctrl+Click, Shift+Click)
- **FR-1.3.5:** Menu de contexto (clique direito) com opções:
  - Copy proxy
  - Copy all proxies
  - Remove proxy
  - Test selected
  - Export selected
- **FR-1.3.6:** Indicador visual de status: ✓ (válido), ✗ (inválido), ⟳ (testando), - (não testado)
- **FR-1.3.7:** Color coding: verde (válido), vermelho (inválido), amarelo (testando), cinza (não testado)

**Requisitos Não-Funcionais:**
- **NFR-1.3.1:** Suportar até 10,000 proxies na tabela sem lag
- **NFR-1.3.2:** Atualização em tempo real durante validação

---

### 3.2 PARTE 2: Validador de Proxies

#### 3.2.1 Importação de Proxies
**Prioridade:** Alta

**Requisitos Funcionais:**
- **FR-2.1.1:** Botão "Import from File" para carregar arquivo .txt
- **FR-2.1.2:** Suporte a formatos:
  - IP:Port (um por linha)
  - Protocol://IP:Port
  - IP:Port:Username:Password
  - Protocol://Username:Password@IP:Port
- **FR-2.1.3:** Validação de formato ao importar
- **FR-2.1.4:** Opção "Use Scraped Proxies" para validar proxies já buscados
- **FR-2.1.5:** Preview dos proxies importados antes da validação

**Requisitos Técnicos:**
- **TR-2.1.1:** Parser robusto com regex para diferentes formatos
- **TR-2.1.2:** Validação de IP com `ipaddress` library
- **TR-2.1.3:** Detecção automática de protocolo quando não especificado

#### 3.2.2 Configuração de Validação
**Prioridade:** Alta

**Requisitos Funcionais:**
- **FR-2.2.1:** Lista de URLs de teste padrões:
  - https://lovable.dev (obrigatório)
  - https://mail.tm (obrigatório)
- **FR-2.2.2:** Botão "Add URL" para adicionar URLs customizadas
- **FR-2.2.3:** Lista editável de URLs com botões Remove/Edit
- **FR-2.2.4:** Campo "Timeout" (1-60 segundos, default: 10)
- **FR-2.2.5:** Campo "Concurrent Threads" (1-100, default: 20)
- **FR-2.2.6:** Checkbox "Test all URLs" ou "Test any URL (OR logic)"
- **FR-2.2.7:** Checkbox "Check anonymity level"
- **FR-2.2.8:** Checkbox "Check geolocation"
- **FR-2.2.9:** Botão "Start Validation" para iniciar testes

**Requisitos Não-Funcionais:**
- **NFR-2.2.1:** Salvar configurações entre sessões
- **NFR-2.2.2:** Validação de URLs (formato correto)

#### 3.2.3 Processo de Validação
**Prioridade:** Crítica

**Requisitos Funcionais:**
- **FR-2.3.1:** Testar cada proxy contra todas as URLs configuradas
- **FR-2.3.2:** Medir tempo de resposta (latência) para cada proxy
- **FR-2.3.3:** Verificar nível de anonimato (Transparent, Anonymous, Elite)
- **FR-2.3.4:** Detectar geolocalização (país, cidade, ISP) se habilitado
- **FR-2.3.5:** Determinar protocolo real suportado
- **FR-2.3.6:** Validar se proxy retorna conteúdo correto (não apenas conecta)
- **FR-2.3.7:** Marcar proxy como válido apenas se passar em TODOS os testes configurados
- **FR-2.3.8:** Atualizar UI em tempo real durante validação
- **FR-2.3.9:** Pausar/Retomar validação
- **FR-2.3.10:** Cancelar validação em andamento

**Requisitos Técnicos:**
- **TR-2.3.1:** Usar `concurrent.futures.ThreadPoolExecutor` ou `asyncio`
- **TR-2.3.2:** Implementar retry logic (máximo 2 tentativas)
- **TR-2.3.3:** Usar `aiohttp` com proxy support
- **TR-2.3.4:** Para detecção de anonimato, comparar IP do proxy com IP real
- **TR-2.3.5:** Integrar com serviço de geolocalização (IP2Location, IPInfo.io API)
- **TR-2.3.6:** Validar resposta HTTP (status code 200, conteúdo esperado)

**Algoritmo de Validação:**
```
Para cada proxy:
  1. Tentar conexão com timeout configurado
  2. Para cada URL de teste:
     a. Enviar request GET através do proxy
     b. Verificar status code (200 OK)
     c. Medir tempo de resposta
     d. Validar conteúdo recebido (opcional)
  3. Se "Test all URLs" habilitado:
     - Proxy válido apenas se TODAS URLs passarem
  4. Se "Test any URL" habilitado:
     - Proxy válido se PELO MENOS UMA URL passar
  5. Se "Check anonymity":
     - Fazer request para serviço que retorna IP
     - Comparar com IP real para determinar nível
  6. Se "Check geolocation":
     - Consultar API de geolocalização
     - Armazenar país, cidade, ISP
  7. Atualizar tabela com resultados
  8. Incrementar contador de progresso
```

**Requisitos Não-Funcionais:**
- **NFR-2.3.1:** Validar 100 proxies em < 120 segundos (com 20 threads)
- **NFR-2.3.2:** Não bloquear UI durante validação
- **NFR-2.3.3:** Memory footprint < 500MB com 1000 proxies

#### 3.2.4 Exportação de Resultados
**Prioridade:** Média

**Requisitos Funcionais:**
- **FR-2.4.1:** Botão "Export Valid Proxies"
- **FR-2.4.2:** Formatos de exportação:
  - TXT (IP:Port, um por linha)
  - CSV (IP, Port, Protocol, Country, Speed, Anonymity)
  - JSON (estrutura completa)
- **FR-2.4.3:** Opção de exportar apenas proxies válidos ou todos
- **FR-2.4.4:** Opção de incluir metadados (timestamp, source, validation_results)
- **FR-2.4.5:** Dialog para escolher local e nome do arquivo

**Requisitos Técnicos:**
- **TR-2.4.1:** Usar `csv` module para CSV
- **TR-2.4.2:** Usar `json` module para JSON
- **TR-2.4.3:** Encoding UTF-8 para todos os arquivos

---

### 3.3 PARTE 3: API REST

#### 3.3.1 Arquitetura da API
**Prioridade:** Alta  
**Framework:** FastAPI

**Requisitos Funcionais:**
- **FR-3.1.1:** API RESTful independente rodando em processo separado
- **FR-3.1.2:** Documentação automática (Swagger UI em /docs)
- **FR-3.1.3:** Versionamento de API (v1)
- **FR-3.1.4:** Autenticação via API Key
- **FR-3.1.5:** Rate limiting por cliente
- **FR-3.1.6:** Logging de todas as requisições

**Requisitos Não-Funcionais:**
- **NFR-3.1.1:** Latência < 500ms para 95% das requisições
- **NFR-3.1.2:** Suportar 100 requisições/segundo
- **NFR-3.1.3:** CORS habilitado para permitir chamadas de browsers

**Requisitos Técnicos:**
- **TR-3.1.1:** FastAPI com Uvicorn como ASGI server
- **TR-3.1.2:** Pydantic para validação de schemas
- **TR-3.1.3:** API Keys armazenados em arquivo config ou database
- **TR-3.1.4:** Middleware para autenticação e rate limiting

#### 3.3.2 Endpoints da API

##### Endpoint: GET /api/v1/health
**Descrição:** Health check da API  
**Autenticação:** Não requerida

**Response 200:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "uptime": 3600
}
```

---

##### Endpoint: POST /api/v1/proxies/scrape
**Descrição:** Buscar proxies de fontes públicas  
**Autenticação:** API Key requerida

**Request Body:**
```json
{
  "quantity": 100,
  "country": "US",
  "protocols": ["http", "https"],
  "sources": ["proxyscrape", "free-proxy-list"]
}
```

**Response 200:**
```json
{
  "success": true,
  "total_found": 98,
  "proxies": [
    {
      "ip": "192.168.1.1",
      "port": 8080,
      "protocol": "http",
      "country": "US",
      "source": "proxyscrape"
    }
  ],
  "execution_time_ms": 5432
}
```

**Parâmetros:**
- `quantity` (integer, 1-1000, default: 100)
- `country` (string, código ISO 2 letras, optional)
- `protocols` (array, values: http/https/socks4/socks5, default: all)
- `sources` (array, fontes específicas, optional)

---

##### Endpoint: POST /api/v1/proxies/validate
**Descrição:** Validar lista de proxies  
**Autenticação:** API Key requerida

**Request Body:**
```json
{
  "proxies": [
    "192.168.1.1:8080",
    "http://10.0.0.1:3128"
  ],
  "test_urls": [
    "https://lovable.dev",
    "https://mail.tm"
  ],
  "timeout": 10,
  "check_anonymity": true,
  "check_geolocation": false,
  "concurrent_tests": 20
}
```

**Response 200:**
```json
{
  "success": true,
  "total_tested": 2,
  "valid_proxies": 1,
  "invalid_proxies": 1,
  "results": [
    {
      "proxy": "192.168.1.1:8080",
      "valid": true,
      "protocol": "http",
      "anonymity": "elite",
      "avg_response_time_ms": 234,
      "test_results": {
        "https://lovable.dev": {
          "success": true,
          "status_code": 200,
          "response_time_ms": 230
        },
        "https://mail.tm": {
          "success": true,
          "status_code": 200,
          "response_time_ms": 238
        }
      },
      "geolocation": null
    },
    {
      "proxy": "10.0.0.1:3128",
      "valid": false,
      "error": "Connection timeout"
    }
  ],
  "execution_time_ms": 10234
}
```

---

##### Endpoint: GET /api/v1/proxies/random
**Descrição:** Obter proxy aleatório válido  
**Autenticação:** API Key requerida

**Query Parameters:**
- `protocol` (string, optional)
- `country` (string, optional)
- `max_response_time` (integer, ms, optional)

**Response 200:**
```json
{
  "proxy": "192.168.1.1:8080",
  "protocol": "http",
  "country": "US",
  "anonymity": "elite",
  "last_checked": "2025-11-07T18:30:00Z",
  "avg_response_time_ms": 234
}
```

**Response 404:**
```json
{
  "error": "No proxy found matching criteria"
}
```

---

##### Endpoint: GET /api/v1/proxies
**Descrição:** Listar todos os proxies armazenados  
**Autenticação:** API Key requerida

**Query Parameters:**
- `page` (integer, default: 1)
- `per_page` (integer, 1-100, default: 50)
- `valid_only` (boolean, default: false)
- `country` (string, optional)
- `protocol` (string, optional)

**Response 200:**
```json
{
  "total": 500,
  "page": 1,
  "per_page": 50,
  "total_pages": 10,
  "proxies": [
    {
      "ip": "192.168.1.1",
      "port": 8080,
      "protocol": "http",
      "country": "US",
      "valid": true,
      "anonymity": "elite",
      "last_checked": "2025-11-07T18:30:00Z",
      "avg_response_time_ms": 234
    }
  ]
}
```

---

##### Endpoint: DELETE /api/v1/proxies
**Descrição:** Limpar base de proxies  
**Autenticação:** API Key requerida

**Query Parameters:**
- `invalid_only` (boolean, default: false)

**Response 200:**
```json
{
  "success": true,
  "deleted_count": 245
}
```

---

##### Endpoint: POST /api/v1/proxies/import
**Descrição:** Importar lista de proxies  
**Autenticação:** API Key requerida

**Request Body:**
```json
{
  "proxies": [
    "192.168.1.1:8080",
    "http://10.0.0.1:3128"
  ],
  "auto_validate": true,
  "validation_urls": ["https://lovable.dev"]
}
```

**Response 200:**
```json
{
  "success": true,
  "imported": 2,
  "duplicates": 0,
  "validation_started": true
}
```

---

#### 3.3.3 Autenticação e Segurança
**Prioridade:** Crítica

**Requisitos Funcionais:**
- **FR-3.3.1:** Geração de API Keys na interface gráfica
- **FR-3.3.2:** Revogação de API Keys
- **FR-3.3.3:** Lista de API Keys ativos na UI
- **FR-3.3.4:** Header de autenticação: `X-API-Key: <key>`
- **FR-3.3.5:** Rate limiting: 100 req/min por API Key (configurável)

**Requisitos Técnicos:**
- **TR-3.3.1:** API Keys com formato UUID4
- **TR-3.3.2:** Hash das keys com bcrypt antes de armazenar
- **TR-3.3.3:** Middleware FastAPI para validação de keys
- **TR-3.3.4:** Rate limiting com `slowapi` library

**Requisitos Não-Funcionais:**
- **NFR-3.3.1:** HTTPS obrigatório em produção
- **NFR-3.3.2:** Logging de tentativas de autenticação falhas
- **NFR-3.3.3:** Bloqueio automático após 5 tentativas falhas

---

### 3.4 Recursos Técnicos Inspirados nos Projetos Sugeridos

#### 3.4.1 mitmproxy
**Inspirações:**
- Implementar modo "intercept" para debug de requisições
- Logging detalhado de tráfego HTTP/HTTPS
- Replay de requisições para testing

**Implementação:**
- Opcional: adicionar modo debug que mostra headers completos
- Salvar histórico de validações para análise posterior

#### 3.4.2 Fireprox-ng
**Inspirações:**
- Rotação automática de IPs usando cloud providers (feature futura)
- Proxy reverso para mascarar origem das requisições

**Implementação:**
- Adicionar opção de "Proxy Chain" para rotear através de múltiplos proxies
- Suportar autenticação upstream de proxies

#### 3.4.3 Gigaproxy
**Inspirações:**
- Bypass de WAF através de rotação inteligente
- Pool de proxies gerenciado automaticamente

**Implementação:**
- Cache de proxies válidos com TTL
- Auto-refresh de proxies expirados
- Score de qualidade para cada proxy

#### 3.4.4 Shadowsocks
**Inspirações:**
- Suporte a protocolo SOCKS5
- Tunneling seguro

**Implementação:**
- Adicionar suporte completo a SOCKS4/SOCKS5
- Opção de testar com diferentes protocolos

#### 3.4.5 Proxy-Bridge
**Inspirações:**
- Multi-level proxy chaining
- Bridge entre diferentes protocolos

**Implementação:**
- Conversor de protocolo (HTTP -> SOCKS e vice-versa)
- Proxy cascading para maior anonimato

---

## 4. Technical Architecture

### 4.1 Technology Stack

**Frontend (GUI):**
- CustomTkinter 0.3+ (interface moderna)
- Pillow (manipulação de imagens/ícones)
- tkinter.ttk (widgets adicionais)

**Backend (Core Logic):**
- Python 3.10+
- aiohttp 3.9+ (requisições assíncronas)
- asyncio (concorrência)
- concurrent.futures (threading)
- requests (fallback para operações síncronas)

**Web Scraping:**
- BeautifulSoup4 (parsing HTML)
- lxml (parser rápido)
- regex (parsing de formatos de proxy)

**API REST:**
- FastAPI 0.104+
- Uvicorn (ASGI server)
- Pydantic (validação de dados)
- slowapi (rate limiting)

**Data Storage:**
- SQLite (persistência local de proxies)
- JSON (configurações)
- Pickle (cache temporário)

**Utilities:**
- ipaddress (validação de IPs)
- validators (validação de URLs)
- python-dotenv (variáveis de ambiente)
- logging (sistema de logs)

### 4.2 System Architecture

```
┌─────────────────────────────────────────────────────┐
│              GUI Layer (CustomTkinter)              │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐  │
│  │  Scraper    │ │  Validator  │ │   Settings  │  │
│  │   Panel     │ │    Panel    │ │    Panel    │  │
│  └─────────────┘ └─────────────┘ └─────────────┘  │
└─────────────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────┐
│           Business Logic Layer                      │
│  ┌──────────────┐  ┌──────────────┐                │
│  │   Proxy      │  │   Validator  │                │
│  │   Scraper    │  │   Engine     │                │
│  └──────────────┘  └──────────────┘                │
└─────────────────────────────────────────────────────┘
                         │
            ┌────────────┼────────────┐
            ▼            ▼            ▼
    ┌─────────────┐ ┌─────────┐ ┌─────────┐
    │  Database   │ │  Cache  │ │  Config │
    │  (SQLite)   │ │         │ │  (JSON) │
    └─────────────┘ └─────────┘ └─────────┘

┌─────────────────────────────────────────────────────┐
│              API Layer (FastAPI)                    │
│  ┌─────────────────────────────────────────────┐   │
│  │  Endpoints: /scrape /validate /proxies      │   │
│  │  Auth Middleware | Rate Limiter             │   │
│  └─────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────┘
```

### 4.3 Data Models

**Proxy Model:**
```python
class Proxy:
    ip: str
    port: int
    protocol: str  # http, https, socks4, socks5
    country: str | None
    city: str | None
    anonymity: str | None  # transparent, anonymous, elite
    source: str
    valid: bool
    last_checked: datetime
    avg_response_time_ms: float | None
    test_results: dict
    created_at: datetime
    updated_at: datetime
```

**ValidationResult Model:**
```python
class ValidationResult:
    proxy: str
    valid: bool
    test_url: str
    status_code: int | None
    response_time_ms: float | None
    error: str | None
    tested_at: datetime
```

**APIKey Model:**
```python
class APIKey:
    key: str  # UUID4
    name: str
    created_at: datetime
    last_used: datetime | None
    rate_limit: int  # requests per minute
    active: bool
```

### 4.4 File Structure

```
proxy-manager/
├── src/
│   ├── __init__.py
│   ├── main.py                    # Entry point
│   ├── gui/
│   │   ├── __init__.py
│   │   ├── main_window.py         # Main GUI window
│   │   ├── scraper_panel.py       # Scraping interface
│   │   ├── validator_panel.py     # Validation interface
│   │   ├── settings_panel.py      # Settings
│   │   └── components/            # Reusable UI components
│   ├── core/
│   │   ├── __init__.py
│   │   ├── scraper.py             # Proxy scraping logic
│   │   ├── validator.py           # Validation engine
│   │   ├── parsers.py             # Proxy format parsers
│   │   └── geolocation.py         # Geo detection
│   ├── api/
│   │   ├── __init__.py
│   │   ├── main.py                # FastAPI app
│   │   ├── endpoints/
│   │   │   ├── proxies.py
│   │   │   ├── scraper.py
│   │   │   └── validator.py
│   │   ├── middleware/
│   │   │   ├── auth.py
│   │   │   └── rate_limit.py
│   │   └── schemas.py             # Pydantic models
│   ├── database/
│   │   ├── __init__.py
│   │   ├── models.py              # SQLAlchemy models
│   │   └── repository.py          # Data access layer
│   └── utils/
│       ├── __init__.py
│       ├── config.py              # Configuration manager
│       ├── logger.py              # Logging setup
│       └── validators.py          # Input validation
├── tests/
│   ├── test_scraper.py
│   ├── test_validator.py
│   └── test_api.py
├── config/
│   ├── settings.json              # App settings
│   ├── api_keys.json              # API keys storage
│   └── sources.json               # Proxy sources config
├── data/
│   └── proxies.db                 # SQLite database
├── logs/
│   └── app.log
├── requirements.txt
├── README.md
└── setup.py
```

---

## 5. User Interface Design

### 5.1 Main Window Layout

```
╔═══════════════════════════════════════════════════════════════╗
║ Proxy Manager v1.0                                      [-][□][X]║
╠═══════════════════════════════════════════════════════════════╣
║ File  Tools  Settings  API  Help                              ║
╠═══════════════════════════════════════════════════════════════╣
║                                                                ║
║ ┌─── Proxy Scraper ──────────────────────────────────────┐   ║
║ │                                                         │   ║
║ │  [ Random Proxies ]  [ Filter by Country ▼ ]          │   ║
║ │                                                         │   ║
║ │  Quantity: [100]    Protocols: [☑HTTP][☑HTTPS]        │   ║
║ │                               [☐SOCKS4][☐SOCKS5]       │   ║
║ │                                                         │   ║
║ │  [Start Scraping]  [Stop]     Progress: ████░░░░ 60%  │   ║
║ └─────────────────────────────────────────────────────────┘   ║
║                                                                ║
║ ┌─── Proxy Validator ────────────────────────────────────┐   ║
║ │                                                         │   ║
║ │  [Import from File]  [Use Scraped Proxies]            │   ║
║ │                                                         │   ║
║ │  Test URLs:                                            │   ║
║ │  • https://lovable.dev             [Remove]           │   ║
║ │  • https://mail.tm                 [Remove]           │   ║
║ │  [+ Add URL]                                           │   ║
║ │                                                         │   ║
║ │  Timeout: [10]s  Threads: [20]  [☑] Check Anonymity  │   ║
║ │                                                         │   ║
║ │  [Start Validation]  [Pause]  [Export Valid Proxies]  │   ║
║ └─────────────────────────────────────────────────────────┘   ║
║                                                                ║
║ ┌─── Results (523 proxies | 145 valid) ─────────────────┐   ║
║ │ IP:Port          │Protocol│Country│Anonymity│Speed│✓ │   ║
║ │ ──────────────────────────────────────────────────────│   ║
║ │ 192.168.1.1:8080 │ HTTP   │ US    │ Elite   │ 234 │ ✓│   ║
║ │ 10.0.0.1:3128    │ HTTPS  │ GB    │ Anon    │ 567 │ ✓│   ║
║ │ 172.16.0.1:1080  │ SOCKS5 │ DE    │ Trans   │ 123 │ ✗│   ║
║ │ ...              │        │       │         │     │  │   ║
║ └─────────────────────────────────────────────────────────┘   ║
║                                                                ║
║ ┌─── Logs ────────────────────────────────────────────────┐  ║
║ │ [INFO] Started scraping from ProxyScrape...            │  ║
║ │ [INFO] Found 98 proxies from ProxyScrape               │  ║
║ │ [INFO] Validation started with 20 threads              │  ║
║ │ [SUCCESS] 192.168.1.1:8080 validated successfully      │  ║
║ └─────────────────────────────────────────────────────────┘  ║
║                                                                ║
╠═══════════════════════════════════════════════════════════════╣
║ Status: Ready | Valid: 145/523 | API: Running on :8000       ║
╚═══════════════════════════════════════════════════════════════╝
```

### 5.2 Settings Panel

```
╔═══════════════════════════════════════════════════════════════╗
║ Settings                                              [Save][X]║
╠═══════════════════════════════════════════════════════════════╣
║                                                                ║
║ ┌─── General ─────────────────────────────────────────────┐  ║
║ │  Theme: ( ) Light  (●) Dark  ( ) System                │  ║
║ │  Language: [English ▼]                                  │  ║
║ │  [☑] Start minimized to tray                           │  ║
║ │  [☑] Check for updates on startup                      │  ║
║ └─────────────────────────────────────────────────────────┘  ║
║                                                                ║
║ ┌─── Scraper Settings ────────────────────────────────────┐  ║
║ │  Default quantity: [100]                                │  ║
║ │  Timeout per source: [30]s                              │  ║
║ │  [☑] Auto-validate after scraping                       │  ║
║ │  [☑] Remove duplicates                                  │  ║
║ │                                                         │  ║
║ │  Enabled Sources:                                       │  ║
║ │  [☑] ProxyScrape    [☑] Free-proxy-list.net            │  ║
║ │  [☑] SSLProxies     [☑] GatherProxy                    │  ║
║ └─────────────────────────────────────────────────────────┘  ║
║                                                                ║
║ ┌─── Validator Settings ──────────────────────────────────┐  ║
║ │  Default timeout: [10]s                                 │  ║
║ │  Default threads: [20]                                  │  ║
║ │  Retry failed proxies: [2] times                        │  ║
║ │  [☑] Check anonymity by default                         │  ║
║ │  [☐] Check geolocation by default                       │  ║
║ │  Geolocation API: [IP2Location ▼]                       │  ║
║ │  API Key: [********************]                        │  ║
║ └─────────────────────────────────────────────────────────┘  ║
║                                                                ║
║ ┌─── API Settings ────────────────────────────────────────┐  ║
║ │  [☑] Enable API server                                  │  ║
║ │  Host: [0.0.0.0]  Port: [8000]                         │  ║
║ │  Rate Limit: [100] req/min per key                     │  ║
║ │                                                         │  ║
║ │  API Keys:                                              │  ║
║ │  • Development Key (****-****-abcd)  [Revoke][Copy]   │  ║
║ │  • Production Key (****-****-efgh)   [Revoke][Copy]   │  ║
║ │  [+ Generate New API Key]                               │  ║
║ └─────────────────────────────────────────────────────────┘  ║
║                                                                ║
╚═══════════════════════════════════════════════════════════════╝
```

---

## 6. Non-Functional Requirements

### 6.1 Performance
- **NFR-6.1.1:** Aplicação deve iniciar em < 3 segundos
- **NFR-6.1.2:** UI deve permanecer responsiva durante todas operações
- **NFR-6.1.3:** Scraping de 100 proxies: < 60 segundos
- **NFR-6.1.4:** Validação de 100 proxies: < 120 segundos (20 threads)
- **NFR-6.1.5:** API latency: < 500ms para 95% das requisições
- **NFR-6.1.6:** Memory usage: < 500MB com 1000 proxies
- **NFR-6.1.7:** Database queries: < 100ms para operações básicas

### 6.2 Reliability
- **NFR-6.2.1:** Uptime da aplicação: > 99%
- **NFR-6.2.2:** Graceful degradation quando fontes de proxy falham
- **NFR-6.2.3:** Auto-recovery de erros não-críticos
- **NFR-6.2.4:** Backup automático de configurações

### 6.3 Usability
- **NFR-6.3.1:** Interface intuitiva, sem necessidade de manual
- **NFR-6.3.2:** Tempo de aprendizado: < 5 minutos
- **NFR-6.3.3:** Tooltips em todos os controles
- **NFR-6.3.4:** Feedback visual para todas as ações

### 6.4 Compatibility
- **NFR-6.4.1:** Windows 10/11
- **NFR-6.4.2:** macOS 11+
- **NFR-6.4.3:** Linux (Ubuntu 20.04+, Debian 11+)
- **NFR-6.4.4:** Python 3.10+

### 6.5 Security
- **NFR-6.5.1:** API Keys criptografados em storage
- **NFR-6.5.2:** HTTPS obrigatório para API em produção
- **NFR-6.5.3:** Input validation em todos os campos
- **NFR-6.5.4:** SQL injection prevention
- **NFR-6.5.5:** Rate limiting contra brute force

### 6.6 Maintainability
- **NFR-6.6.1:** Código modular e bem documentado
- **NFR-6.6.2:** Cobertura de testes: > 70%
- **NFR-6.6.3:** Logging completo de operações
- **NFR-6.6.4:** Configurações separadas do código

---

## 7. Dependencies & Integrations

### 7.1 Python Packages
```
customtkinter>=0.3.0
aiohttp>=3.9.0
fastapi>=0.104.0
uvicorn>=0.24.0
pydantic>=2.0.0
beautifulsoup4>=4.12.0
lxml>=4.9.0
requests>=2.31.0
SQLAlchemy>=2.0.0
slowapi>=0.1.9
python-dotenv>=1.0.0
Pillow>=10.0.0
validators>=0.22.0
```

### 7.2 External APIs (Optional)
- **IP2Location** - Geolocation detection
- **IPInfo.io** - Alternative geolocation
- **ProxyScrape API** - Proxy source
- **PubProxy API** - Proxy source

### 7.3 Proxy Sources
- ProxyScrape.com
- Free-proxy-list.net
- SSLProxies.org
- GatherProxy.com
- Spys.one
- PubProxy.com
- HideMy.name

---

## 8. Testing Strategy

### 8.1 Unit Tests
- Scraper functions (parsing, deduplication)
- Validator logic (protocol detection, anonymity check)
- API endpoints (CRUD operations)
- Database operations
- Utility functions

### 8.2 Integration Tests
- GUI + Core logic integration
- API + Database integration
- Scraper + Validator pipeline
- End-to-end proxy lifecycle

### 8.3 Manual Testing
- UI usability testing
- Cross-platform compatibility
- Performance under load
- Error scenarios

### 8.4 Test Data
- Sample proxy lists (valid/invalid)
- Mock API responses
- Test URLs with predictable behavior

---

## 9. Deployment & Distribution

### 9.1 Packaging
- **PyInstaller** para criar executáveis standalone
- Suporte a Windows (.exe), macOS (.app), Linux (AppImage)
- Installer scripts para cada plataforma

### 9.2 Distribution Channels
- GitHub Releases
- PyPI package (opcional)
- Website próprio com downloads

### 9.3 Installation Requirements
- Python 3.10+ (se rodando source)
- 100MB espaço em disco
- 512MB RAM mínimo

---

## 10. Future Enhancements (Roadmap)

### Phase 2 (v2.0)
- **Cloud Proxy Integration** - AWS/Azure/GCP proxy rotation
- **Proxy Pools** - Gerenciamento de pools categorizados
- **Scheduler** - Validação automática agendada
- **Dashboard Web** - Interface web além da desktop
- **Webhook Support** - Notificações de eventos

### Phase 3 (v3.0)
- **Machine Learning** - Predição de qualidade de proxy
- **Distributed Validation** - Cluster de validadores
- **Premium Proxy Support** - Integração com serviços pagos
- **Browser Extension** - Controle via extensão de navegador
- **Docker Support** - Container deployment

---

## 11. Success Criteria

### Launch Criteria
- [ ] Todas as features da Parte 1, 2 e 3 implementadas
- [ ] Testes unitários com > 70% coverage
- [ ] Documentação completa (README, API docs)
- [ ] Testado em Windows, macOS e Linux
- [ ] Performance metrics atendidos
- [ ] Zero critical bugs

### Post-Launch Metrics (3 meses)
- 1000+ downloads
- < 5% crash rate
- Feedback positivo de usuários (> 4.0/5.0)
- 90% das features utilizadas ativamente
- API adoption por desenvolvedores externos

---

## 12. Risks & Mitigation

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| Fontes de proxy bloqueiam scraping | Alto | Média | Múltiplas fontes, rate limiting, user agents rotativos |
| Performance degradation com muitos proxies | Médio | Média | Pagination, indexing, cache |
| API rate limiting/custos | Baixo | Baixa | Limites configuráveis, alertas |
| Cross-platform compatibility issues | Médio | Média | Testes extensivos, CI/CD |
| Segurança das API Keys | Alto | Baixa | Encryption, secure storage |

---

## 13. Glossary

- **Proxy**: Servidor intermediário que atua entre cliente e servidor
- **Anonymity Level**: Elite (high), Anonymous (medium), Transparent (low)
- **Scraping**: Coleta automatizada de dados
- **SOCKS**: Protocol de proxy que suporta TCP
- **Geolocation**: Localização geográfica baseada em IP
- **Rate Limiting**: Limitação de requisições por tempo
- **API Key**: Chave de autenticação para API

---

## 14. Appendix

### A. Sample Proxy Formats
```
# IP:Port
192.168.1.1:8080

# Protocol://IP:Port
http://192.168.1.1:8080
socks5://192.168.1.1:1080

# With Authentication
http://username:password@192.168.1.1:8080
socks5://user:pass@192.168.1.1:1080
```

### B. API Authentication Example
```bash
curl -X POST "http://localhost:8000/api/v1/proxies/scrape" \
  -H "X-API-Key: your-api-key-here" \
  -H "Content-Type: application/json" \
  -d '{
    "quantity": 50,
    "country": "US",
    "protocols": ["http", "https"]
  }'
```

### C. Configuration File Example
```json
{
  "scraper": {
    "default_quantity": 100,
    "timeout": 30,
    "auto_validate": true,
    "sources": ["proxyscrape", "free-proxy-list"]
  },
  "validator": {
    "default_timeout": 10,
    "default_threads": 20,
    "check_anonymity": true,
    "check_geolocation": false
  },
  "api": {
    "enabled": true,
    "host": "0.0.0.0",
    "port": 8000,
    "rate_limit": 100
  }
}
```

---

**Document Version History:**
- v1.0 - 2025-11-07 - Initial PRD creation

**Approvals:**
- [ ] Product Manager
- [ ] Tech Lead
- [ ] UX Designer
- [ ] QA Lead
