# RAG Assistant

Uma solução completa de **Retrieval-Augmented Generation (RAG)** para análise de documentos financeiros usando **FastAPI**, **Streamlit** e **Chroma DB**.

![Version](https://img.shields.io/badge/version-1.0.0-blue)
![Python](https://img.shields.io/badge/python-3.12+-green)
![Docker](https://img.shields.io/badge/docker-supported-blue)
![License](https://img.shields.io/badge/license-MIT-green)

---

## 🎯 O que é?

Finance RAG Assistant permite:

✅ **Upload de PDFs de documentos financeiros** (relatórios, earnings releases, etc)  
✅ **Processamento automático** com OCR e extração de metadata  
✅ **Armazenamento vetorial** com Chroma DB  
✅ **Perguntas e Respostas** usando IA (Multi-Agent Pipeline)  
✅ **Interface web interativa** com Streamlit  
✅ **API REST completa** com FastAPI  
✅ **Containerizado** com Docker & Docker Compose  

---

## Quick Start (5 minutos)

### Opção 1: Docker (Recomendado)

```bash
# 1. Clone o repositório
git clone https://github.com/seu_usuario/rag-assistant.git
cd rag-assistant

# 2. Configure variáveis de ambiente
cp .env.example .env
# Edite .env e adicione sua OPENAI_API_KEY

# 3. Build e inicie
docker-compose build --no-cache
docker-compose up -d

# 4. Acesse
# Streamlit UI:   http://localhost:8501
# API Swagger:    http://localhost:8000/docs
# Chroma Admin:   http://localhost:8080
```

### Opção 2: Local (sem Docker)

```bash
# 1. Clone
git clone https://github.com/seu_usuario/rag-assistant.git
cd rag-assistant

# 2. Crie ambiente virtual
python3.12 -m venv env
source env/bin/activate  # ou: env\Scripts\activate (Windows)

# 3. Instale dependências
pip install -r requirements.txt

# 4. Configure variáveis
cp .env
# Edite .env

# 5. Inicie a API (Terminal 1)
uvicorn src.app.api.main:app --reload --host 0.0.0.0 --port 8000

# 6. Inicie Streamlit (Terminal 2)
streamlit run streamlit_app.py

# 7. Acesse
# Streamlit: http://localhost:8501
# API:       http://localhost:8000/docs
```

---

## 📋 Pré-requisitos

### Para Docker
- [Docker Desktop](https://www.docker.com/products/docker-desktop) (MacOS/Windows) ou Docker Engine (Linux)
- Docker Compose v2.0+
- ~2GB de espaço em disco

### Para Local
- Python 3.10+
- pip ou conda
- OpenAI API Key ([obter aqui](https://platform.openai.com/api-keys))
- ~1GB de espaço em disco

---

## 📁 Estrutura do Projeto

```
rag-assistant/
├── src/app/
│   ├── api/                 # FastAPI backend
│   │   ├── main.py
│   │   └── routers/
│   │       ├── ask.py       # Q&A endpoint
│   │       └── ingest.py    # PDF ingestion endpoints
│   ├── agents/              # Multi-agent pipeline
│   │   ├── pipeline.py
│   │   ├── qa_agent.py
│   │   ├── extractor_agent.py
│   │   └── risk_agent.py
│   ├── ingestion/           # PDF processing
│   │   ├── pipeline.py
│   │   ├── pdf_to_md.py     # PDF → Markdown
│   │   ├── chunking.py      # Texto → Chunks
│   │   └── metadata.py
│   ├── retrieval/           # Vector search
│   ├── storage/             # Chroma DB
│   ├── core/                # Utilities
│   ├── config/              # Settings
│   └── prompts/             # LLM prompts
├── streamlit_app.py         # Web UI
├── docker-compose.yml       # Container orchestration
├── Dockerfile               # Container image
├── requirements.txt         # Python dependencies
├── .env.example             # Environment template
├── Makefile                 # Atalhos úteis
└── README.md               # Este arquivo
```

---

## 🔧 Configuração

### Variáveis de Ambiente

Crie arquivo `.env`:

```env
# OpenAI
OPENAI_API_KEY=sk-xxx_sua_chave_aqui


# Chroma Database
CHROMA_HOST=chroma
CHROMA_PORT=8000
CHROMA_COLLECTION=documents

# Logging
LOG_LEVEL=INFO
```

---

## 💻 Como Usar

### 📤 Upload de PDFs

**Via Streamlit UI:**

1. Acesse http://localhost:8501
2. Vá para tab **"📤 Ingestão de PDFs"**
3. Selecione 1 ou mais arquivos PDF
4. Clique **"🚀 Ingerir PDFs"**
5. Aguarde processamento

**Via cURL:**

```bash
# Upload único
curl -X POST "http://localhost:8000/ingest/pdf" \
  -F "file=@documento.pdf"

# Upload em lote
curl -X POST "http://localhost:8000/ingest/batch" \
  -F "files=@doc1.pdf" \
  -F "files=@doc2.pdf"
```



### 🔍 Fazer Perguntas

**Via Streamlit UI:**

1. Vá para tab **"🔍 Perguntas & Respostas"**
2. Digite sua pergunta
3. Clique **"🔍 Buscar Resposta"**
4. Veja resposta + histórico

**Via cURL:**

```bash
curl -X POST "http://localhost:8000/ask/" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Qual foi o faturamento da Apple em 2024?"
  }'
```


---

## 🎨 Interface Web (Streamlit)

### Tab 1: 📤 Ingestão de PDFs

- Selecione 1 ou múltiplos PDFs
- Detecção automática de roteamento:
  - 1 PDF → `/ingest/pdf`
  - 2+ PDFs → `/ingest/batch`
- Visualize status e resultados
- Doc ID e números de chunks

### Tab 2: 🔍 Q&A

- Digite perguntas sobre documentos
- Veja respostas com metadata
- Histórico de perguntas (em sessão)
- Intent detection

---

## 🔌 API REST

### Endpoints Disponíveis

#### **POST** `/ingest/pdf` - Upload único
```bash
curl -X POST http://localhost:8000/ingest/pdf \
  -F "file=@documento.pdf"
```

**Response:**
```json
{
  "success": true,
  "doc_id": "a1b2c3d4e5f6",
  "n_chunks": 42,
  "message": "PDF 'documento.pdf' ingerido com sucesso",
  "error": null
}
```

---

#### **POST** `/ingest/batch` - Upload em lote
```bash
curl -X POST http://localhost:8000/ingest/batch \
  -F "files=@doc1.pdf" \
  -F "files=@doc2.pdf"
```

**Response:**
```json
{
  "total": 2,
  "successful": 2,
  "failed": 0,
  "results": [
    {
      "success": true,
      "message": "PDF 'doc1.pdf' ingerido com sucesso",
      "error": null
    },
    {
      "success": true,
      "message": "PDF 'doc2.pdf' ingerido com sucesso",
      "error": null
    }
  ]
}
```

---

#### **POST** `/ask/` - Fazer pergunta
```bash
curl -X POST http://localhost:8000/ask/ \
  -H "Content-Type: application/json" \
  -d '{"question": "Qual é o maior risco?"}'
```

**Response:**
```json
{
  "answer": "De acordo com os documentos, o maior risco é...",
  "intent": "risk_analysis",
  "metadata_used": {
    "company": "Apple",
    "doc_date": "2024"
  }
}
```

---

## 🏗️ Arquitetura

```
┌─────────────────────────────────────────────────────┐
│                  User Interface                      │
│  (Streamlit Web App - http://localhost:8501)        │
└──────────────────────┬──────────────────────────────┘
                       │ (HTTP)
┌──────────────────────▼──────────────────────────────┐
│              FastAPI Backend                        │
│  (API - http://localhost:8000)                      │
│  ├── /ingest/pdf (upload único)                    │
│  ├── /ingest/batch (upload lote)                   │
│  └── /ask/ (perguntas)                             │
└──────────┬──────────────────┬──────────────────────┘
           │                  │
    ┌──────▼────────┐   ┌─────▼──────────┐
    │  Ingestion    │   │    Retrieval   │
    │  Pipeline     │   │    Pipeline    │
    ├─ PDF→MD      │   ├─ Vector Search│
    ├─ Chunking    │   ├─ Metadata     │
    ├─ Metadata    │   └─ Filtering    │
    └─ Embeddings  │
           │
    ┌──────▼──────────────────────────────┐
    │      Chroma Vector Database         │
    │  (Storage - http://localhost:8080)  │
    │  ├─ Embeddings                      │
    │  ├─ Documents                       │
    │  └─ Metadata                        │
    └─────────────────────────────────────┘
```

---

## 🐳 Comandos Docker



### Com Docker Compose direto

```bash
docker-compose build --no-cache    # Build
docker-compose up -d               # Iniciar
docker-compose down                # Parar
docker-compose logs -f             # Logs
docker-compose ps                  # Status
```

---


### Checklist

- [ ] OPENAI_API_KEY em secret manager
- [ ] .env não commitado (.gitignore)
- [ ] Logging de auditoria ativo





