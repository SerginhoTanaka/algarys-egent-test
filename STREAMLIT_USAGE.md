# 🎨 Streamlit Web Interface

Interface web interativa para o Finance RAG Assistant.

## 🚀 Como Executar

### Opção 1: Script bash
```bash
chmod +x run_streamlit.sh
./run_streamlit.sh
```

### Opção 2: Comando direto
```bash
source env/bin/activate
streamlit run streamlit_app.py
```

A aplicação abrirá em: **http://localhost:8501**

---

## 📋 Funcionalidades

### 📤 Tab 1: Ingestão de PDFs

**Upload de Documentos:**
- Selecione 1 ou mais arquivos PDF
- Detecção automática de quantidade de arquivos
- Roteamento inteligente:
  - **1 PDF** → Usa `/ingest/pdf` (upload único)
  - **Múltiplos PDFs** → Usa `/ingest/batch` (upload em lote)

**Resposta:**
- Status de sucesso/erro
- Document ID
- Número de chunks criados
- Detalhes de cada arquivo (em caso de batch)

### 🔍 Tab 2: Perguntas & Respostas

**Fazer Perguntas:**
- Caixa de texto para perguntas
- Chamada à API `/ask/`
- Exibição da resposta com formatting

**Informações Adicionais:**
- Intent detecção
- Metadados utilizados
- Histórico de perguntas

---

## ⚙️ Configuração

### Variáveis de Ambiente

```bash
# URL da API (padrão: http://localhost:8000)
export API_URL="http://localhost:8000"
```

### Ou editar no Streamlit

Na sidebar da aplicação, você pode mudar a URL da API em tempo real.

---

## 📋 Pré-requisitos

- Python 3.10+
- API rodando em `http://localhost:8000`
- Dependências instaladas: `pip install -r requirements.txt`

---

## 🔄 Fluxo de Uso

```
1. Iniciar API:
   uvicorn src.app.api.main:app --reload

2. Iniciar Streamlit (outro terminal):
   streamlit run streamlit_app.py

3. Abrir navegador:
   http://localhost:8501

4. Upload de PDFs:
   - Selecione 1+ arquivos
   - Clique "Ingerir PDFs"
   - Espere resultado

5. Fazer perguntas:
   - Digite pergunta
   - Clique "Buscar Resposta"
   - Veja resposta + histórico
```

---

## 🎯 Exemplo de Uso

### Via Streamlit UI:

1. **Ingestão:**
   - Upload: `APPLE_Q3_2024.pdf`, `NVIDIA_Q3_2024.pdf`
   - Detecta 2 PDFs → Usa `/ingest/batch`
   - Resposta: "✅ 2 arquivos processados com sucesso"

2. **Q&A:**
   - Pergunta: "Qual empresa teve maior faturamento?"
   - Resposta: "Apple teve faturamento de..."
   - Histórico salvo automaticamente

---

## 📊 Estrutura da App

```
streamlit_app.py
├── Config da página
├── Tab 1: Ingestão
│   ├── Uploader de arquivos
│   ├── Detecção de quantidade
│   ├── Roteamento (pdf vs batch)
│   └── Exibição de resultados
└── Tab 2: Q&A
    ├── Input de pergunta
    ├── Chamada à API
    ├── Exibição de resposta
    └── Histórico
```

---

## 🐛 Troubleshooting

### Erro: "URLError: [Errno 111] Connection refused"
```
✓ Verifique se a API está rodando
✓ Confirme a URL na sidebar (padrão: http://localhost:8000)
```

### Erro: "ModuleNotFoundError: No module named 'streamlit'"
```bash
pip install streamlit
# ou
pip install -r requirements.txt
```

### Timeout na ingestão de PDFs grandes
```bash
# Aumentar timeout editando streamlit_app.py
timeout=300  # 5 minutos
```

---

## 🎨 Customizações

Editar `streamlit_app.py` para:
- Mudar cores/temas
- Adicionar mais tabs
- Modificar layout
- Adicionar mais endpoints

---

## 📝 Notas

- O histórico de perguntas é mantido em memória (por sessão)
- Para análise completa, acesse: `http://localhost:8000/docs` (Swagger)
- ReDoc disponível em: `http://localhost:8000/redoc`
