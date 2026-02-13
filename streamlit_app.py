import streamlit as st
import requests
import os
from pathlib import Path

# Configuração da página
st.set_page_config(
    page_title="RAG Assistant",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilo customizado
st.markdown("""
    <style>
    .main {
        padding: 2rem;
    }
    .stTabs [data-baseweb="tab-list"] button [data-testid="stMarkdownContainer"] p {
        font-size: 1.2rem;
    }
    </style>
""", unsafe_allow_html=True)

# Config da API
API_URL = os.getenv("API_URL", "http://localhost:8000")

# Header
st.title("📊 RAG Assistant")
st.markdown("---")

# Sidebar com configurações
with st.sidebar:
    st.header("⚙️ Configurações")
    api_url_input = st.text_input(
        "URL da API",
        value=API_URL,
        help="URL base para conexão com a API"
    )
    st.info(f"API conectada em: {api_url_input}")

# Tabs principais
tab1, tab2 = st.tabs(["📤 Ingestão de PDFs", "🔍 Perguntas & Respostas"])

# TAB 1: Ingestão
with tab1:
    st.header("Carregar Documentos")
    
    uploaded_files = st.file_uploader(
        "Selecione um ou mais arquivos PDF",
        type=["pdf"],
        accept_multiple_files=True,
        help="Use Ctrl+Click para selecionar múltiplos arquivos"
    )
    
    if uploaded_files:
        st.info(f"📁 {len(uploaded_files)} arquivo(s) selecionado(s)")
        
        # Botão para ingerir
        if st.button("🚀 Ingerir PDFs", use_container_width=True, type="primary"):
            
            if len(uploaded_files) == 1:
                # Endpoint de PDF único
                st.info("📄 Usando endpoint de upload único...")
                
                pdf_file = uploaded_files[0]
                
                try:
                    with st.spinner(f"Processando {pdf_file.name}..."):
                        files = {"file": (pdf_file.name, pdf_file, "application/pdf")}
                        response = requests.post(
                            f"{api_url_input}/ingest/pdf",
                            files=files,
                            timeout=300
                        )
                    
                    if response.status_code == 200:
                        result = response.json()
                        st.success(f"✅ {result['message']}")
                        
                        with st.expander("📊 Detalhes"):
                            col1, col2 = st.columns(2)
                            with col1:
                                st.metric("Doc ID", result.get('doc_id', 'N/A'))
                            with col2:
                                st.metric("Chunks", result.get('n_chunks', 'N/A'))
                    else:
                        st.error(f"❌ Erro: {response.text}")
                
                except Exception as e:
                    st.error(f"❌ Erro na conexão: {str(e)}")
            
            else:
                # Endpoint de batch
                st.info(f"📦 Usando endpoint de batch para {len(uploaded_files)} arquivos...")
                
                try:
                    with st.spinner(f"Processando {len(uploaded_files)} arquivos..."):
                        files = [
                            ("files", (f.name, f, "application/pdf"))
                            for f in uploaded_files
                        ]
                        response = requests.post(
                            f"{api_url_input}/ingest/batch",
                            files=files,
                            timeout=600
                        )
                    
                    if response.status_code == 200:
                        result = response.json()
                        
                        st.success(f"✅ Lote processado!")
                        
                        # Resumo
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Total", result['total'])
                        with col2:
                            st.metric("Sucesso", result['successful'], 
                                     delta=None, delta_color="off")
                        with col3:
                            st.metric("Falhas", result['failed'], 
                                     delta=None, delta_color="off")
                        
                        # Detalhes de cada arquivo
                        st.subheader("Detalhes por Arquivo")
                        for idx, item in enumerate(result['results'], 1):
                            status_icon = "✅" if item['success'] else "❌"
                            with st.expander(f"{status_icon} {uploaded_files[idx-1].name}"):
                                st.write(item['message'])
                                if item['error']:
                                    st.error(f"**Erro:** {item['error']}")
                    else:
                        st.error(f"❌ Erro na requisição: {response.text}")
                
                except Exception as e:
                    st.error(f"❌ Erro na conexão: {str(e)}")

# TAB 2: Q&A
with tab2:
    st.header("Fazer Perguntas")
    st.markdown("Faça perguntas sobre os documentos carregados")
    
    # Caixa de entrada
    question = st.text_area(
        "Sua pergunta:",
        placeholder="Ex: Qual foi o faturamento da Apple no Q3 2024?",
        height=100
    )
    
    if st.button("🔍 Buscar Resposta", use_container_width=True, type="primary"):
        if not question.strip():
            st.warning("⚠️ Digite uma pergunta!")
        else:
            try:
                with st.spinner("Buscando resposta..."):
                    response = requests.post(
                        f"{api_url_input}/ask/",
                        json={"question": question},
                        timeout=60
                    )
                
                if response.status_code == 200:
                    result = response.json()
                    
                    st.success("✅ Resposta encontrada!")
                    
                    # Resposta principal
                    st.subheader("Resposta")
                    st.markdown(f"> {result['answer']}")
                    
                    # Detalhes adicionais
                    col1, col2 = st.columns(2)
                    with col1:
                        if result.get('intent'):
                            st.info(f"**Intent:** {result['intent']}")
                    with col2:
                        if result.get('metadata_used'):
                            st.info(f"**Metadados:** {result['metadata_used']}")
                    
                    # Histórico (opcional)
                    if "chat_history" not in st.session_state:
                        st.session_state.chat_history = []
                    
                    st.session_state.chat_history.append({
                        "question": question,
                        "answer": result['answer']
                    })
                    
                    st.divider()
                    
                else:
                    st.error(f"❌ Erro na API: {response.text}")
            
            except Exception as e:
                st.error(f"❌ Erro na conexão: {str(e)}")
                st.info(f"💡 Verifique se a API está rodando em `{api_url_input}`")
    
    # Histórico de perguntas
    if "chat_history" in st.session_state and st.session_state.chat_history:
        st.divider()
        st.subheader("📜 Histórico")
        
        for i, item in enumerate(st.session_state.chat_history, 1):
            with st.expander(f"Pergunta {i}: {item['question'][:50]}..."):
                st.markdown(f"**Q:** {item['question']}")
                st.markdown(f"**A:** {item['answer']}")

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #888;">
    <p>RAG Assistant v1.0 | Powered by Streamlit + FastAPI</p>
</div>
""", unsafe_allow_html=True)
    