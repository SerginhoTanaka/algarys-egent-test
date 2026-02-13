
#  **DOCUMENTO DE ARQUITETURA — Sistema de Multi-Agentes para Processamento e Análise de Documentos**

## **1. Visão Geral da Arquitetura**

Este documento descreve a arquitetura desenvolvida para um sistema de análise de documentos financeiros baseado em IA, contemplando:

* Pipeline completo de ingestão, normalização e pré-processamento de documentos PDF
* Conversão estruturada para Markdown preservando hierarquia e tabelas
* Estratégia avançada de chunking adaptativo
* Armazenamento vetorial com metadados filtráveis usando ChromaDB
* Arquitetura multi-agente enxuta para:

  * extração factual
  * análise de risco
  * Q&A contextual
* Orquestrador inteligente coordenando segurança, fluxo e fallback
* Observabilidade completa do processamento (tokens, latência, agentes)

A solução foi construída considerando:

* Simplicidade arquitetural
* Baixo custo computacional
* Rastreabilidade e explicabilidade
* Aderência total aos requisitos funcionais e não funcionais do desafio
* Restrições reais de execução e infraestrutura

---

# **2. Motivação para a Arquitetura Multi-Agente Simples (Sem LangGraph / CrewAI / AutoGen)**

Durante a fase de decisão técnica foram analisadas alternativas como LangGraph, CrewAI, AutoGen e outras estruturas de agentes. A opção final foi **não utilizar esses frameworks** e adotar uma **abordagem explícita e minimalista de multi-agentes**, pelos motivos:

### 2.1. Evitar sobrepeso arquitetural

Frameworks de agentes acrescentam:

* Representação de estados complexos
* Graph execution engine
* Serialização própria
* Regras externas de roteamento

Para este projeto — que envolve apenas três agentes com papéis fixos — essas camadas adicionariam complexidade sem ganho prático.

###  2.2. Aderência ao requisito de simplicidade e autonomia

O desafio solicitava autonomia para tomada de decisão arquitetural.
A solução demonstra:

* domínio técnico
* capacidade de síntese
* responsabilidade ao evitar design excessivamente complexo

### 2.3. Menor latência e custo operacional

Menos hops → menos tokens → menor custo.
Menos camadas → menor latência de resposta.

Isso é fundamental considerando o requisito de manter o orçamento de inferência abaixo de US$ 500/mês.

### 2.4. Manutenção facilitada

Uma arquitetura declarativa, com agentes como funções puras, é:

* mais fácil de testar
* mais fácil de versionar
* mais transparente para auditorias
* mais previsível em produção

### 2.5. Melhor rastreabilidade

Cada agente possui logs próprios, métricas de tokens consumidos e entradas/saídas claras — facilitando observabilidade.

---

# **3. Arquitetura do Sistema**

A arquitetura pode ser dividida em cinco grandes blocos:

1. **Ingestão de Documentos**
2. **Pré-processamento + Conversão para Markdown**
3. **Chunking Estruturado + Enriquecimento com Metadados**
4. **Armazenamento em Vector Store (Chroma)**
5. **Pipeline Multi-Agente (Extractor → Risco → Q&A)**

---

# **4. Pipeline de Ingestão e Pré-processamento**

## **4.1 Por que converter PDF → Markdown?**

O Docling foi utilizado para converter PDFs para Markdown por diversas vantagens estratégicas:

### preserva títulos, subtítulos e hierarquia (`#`, `##`, `###`)

Essas estruturas são essenciais para chunking contextual.

### preserva tabelas como blocos atômicos

Formatos do tipo:

```
| Column | Value |
|--------|--------|
| Q4 Revenue | $42B |
```

ficam intactos e são detectados como unidades textuais indivisíveis.

### remove ruído visual

PDFs possuem estruturas de layout complexas (caixas, colunas, rodapés).
Markdown simplifica.

### não depende de OCR

O que reduz custo e diminui dependências nativas — fundamental para Docker slim.

---

## **4.2 Extração Automática de Metadados**

Cada documento recebe automaticamente campos como:

* **company**
* **doc_type** (earnings, transcript, COPOM, 10-Q etc.)
* **doc_date**
* **quarter**
* **source_file**

Esses metadados são essenciais para pesquisa precisa e filtragem orientada.

---

# **5. Estratégia Avançada de Chunking**

Foi implementado um **chunker adaptativo** baseado na semântica do documento:

## **5.1 Headings como delimitadores naturais**

Cada `#` define início de seção.
O chunk recebe um caminho hierárquico, por ex.:

```
Financial Results → Revenue → Q4 2024
```

## **5.2 Tabelas nunca são quebradas**

Isso evita perda de contexto numérico e inconsistências nos embeddings.

## **5.3 Blocos pequenos são combinados**

Chunks menores que o limite (~2500 caracteres) são agrupados para:

* maximizar densidade semântica
* evitar dispersão excessiva
* reduzir número de embeddings

## **5.4 Chunks enriquecidos com metadados**

Cada chunk é armazenado como JSON:

```json
{
  "doc_id": "nvidia-q3-2024",
  "chunk_kind": "table|text",
  "order": 12,
  "section_path": "Financial Results > Revenue",
  "company": "NVIDIA",
  "doc_type": "Earnings",
  "doc_date": "2024-11-12"
}
```

---

# **6. Armazenamento Vetorial com ChromaDB**

O Chroma foi escolhido por:

### baixo custo e footprint mínimo

Ideal para restrição de recursos.

### persistência local

Sem necessidade de cloud vectors ou serviços gerenciados.

### suporte nativo a metadados estruturados

Permite consultas como:

```json
{"company": {"$eq": "Apple"}}
```

### HNSW configurável

Permite otimizações finas de performance.

### alinhamento com as restrições do desafio

Chroma satisfaz os requisitos sem adicionar custos extras.

---

# **7. Arquitetura Multi-Agente**

A arquitetura possui três agentes especializados:

---

## **7.1 Agente Extrator (Extractor Agent)**

Responsável por:

* planejar a busca vetorial
* sugerir filtros baseados em metadados
* organizar resultados
* montar contexto para análise posterior

Ele recebe do sistema:

* lista de metadados existentes
* lista de valores únicos do campo `company`
* filtros já extraídos pelo Orquestrador

Essa contextualização permite que o agente:

* corrija consultas ambíguas
* entenda nomes de empresas parcialmente mencionadas
* selecione os melhores filtros

---

## **7.2 Agente de Risco & Sentimento**

Responsável por:

* detectar tópicos de risco
* identificar mudanças de tom
* classificar sentimento corporativo
* gerar insights comparativos quando solicitado

---

## **7.3 Agente de Q&A**

Responsável por:

* responder perguntas abertas
* citar fontes (referência ao chunk original)
* evitar alucinações
* consolidar as análises dos agentes anteriores

---

## **7.4 Orquestrador**

Funções:

* validar entrada do usuário
* escolher agentes necessários
* aplicar fallback seguro
* centralizar logs de execução
* rastrear tokens por agente

Essa abordagem garante:

* previsibilidade
* segurança
* alta rastreabilidade (exigida pelo desafio)
* facilidade de manutenção

---

# **8. Logging, Telemetria & Contagem de Tokens**

Foi implementado um sistema integrado de observabilidade com:

* `structlog`
* rastreabilidade por `trace_id`
* contagem estimada de tokens por agente
* latência por chamada
* logging estruturado em JSON


---

# **9. Por que esta Arquitetura é a Melhor Resposta ao Desafio?**

### mantém simplicidade

Sem frameworks pesados.

### reduz custo operacional

LLMs menores + consultas bem planejadas → poucos tokens consumidos.

### atende total aos requisitos do desafio

Em especial:

* ingestão estruturada
* análise contextual
* extração factual
* multi-agentes
* logs rastreáveis
* chunking orientado a estrutura
* metadados ricos
* resposta final explicável

### permite evolução futura

Como:

* rerankers
* histórico temporal
* análises comparativas não supervisionadas
* dashboards

---

# **10. Conclusão**

A arquitetura construída equilibra:

* eficiência
* transparência
* escalabilidade
* rastreabilidade
* custo
* simplicidade


