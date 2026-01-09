import streamlit as st
import google.generativeai as genai
from PIL import Image

# 1. Configuração da Página
st.set_page_config(
    page_title="ArchViz AI Director",
    page_icon="🏢",
    layout="wide"
)

# 2. Configuração da API do Google Gemini
# Tenta pegar a chave dos Segredos do Streamlit
try:
    if "GOOGLE_API_KEY" in st.secrets:
        api_key = st.secrets["GOOGLE_API_KEY"]
        genai.configure(api_key=api_key)
        api_configured = True
    else:
        st.warning("⚠️ API Key não encontrada nos Segredos.")
        api_configured = False
except Exception as e:
    st.error(f"Erro ao configurar API: {e}")
    api_configured = False

# Título e Subtítulo
st.title("🏢 ArchViz AI Director")
st.caption("Seu assistente de direção de arte para Visualização Arquitetônica.")

# 3. Interface Principal
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("1. Upload do Projeto")
    uploaded_file = st.file_uploader("Arraste seu render ou croqui aqui", type=["jpg", "jpeg", "png"])
    
    if uploaded_file is not None:
        # Exibe a imagem carregada
        image = Image.open(uploaded_file)
        st.image(image, caption="Imagem Carregada", use_container_width=True)

with col2:
    st.subheader("2. O que você precisa?")
    
    # Prompt padrão focado em ArchViz
    default_prompt = (
        "Atue como um Diretor de Arte Sênior em ArchViz. "
        "Analise esta imagem em termos de iluminação, composição, texturas e realismo. "
        "Liste 3 pontos fortes e 3 sugestões de melhoria técnica para tornar a imagem mais fotorealista e impactante."
    )
    
    prompt = st.text_area("Comando para a IA:", value=default_prompt, height=150)
    
    generate_btn = st.button("🎬 Analisar Imagem", type="primary")

# 4. Lógica de Geração
if generate_btn:
    if not api_configured:
        st.error("Por favor, configure a GOOGLE_API_KEY nos 'Secrets' do Streamlit para continuar.")
    elif not uploaded_file:
        st.warning("Por favor, faça o upload de uma imagem primeiro.")
    elif not prompt:
        st.warning("Por favor, digite um comando.")
    else:
        try:
            with st.spinner("O Diretor de Arte está analisando sua imagem..."):
                # Configura o modelo (Gemini 1.5 Flash é rápido e bom com imagens)
                model = genai.GenerativeModel('gemini-1.5-flash')
                
                # Envia o prompt de texto + a imagem carregada
                response = model.generate_content([prompt, image])
                
                # Exibe a resposta
                st.success("Análise concluída!")
                st.markdown("### 📋 Relatório do Diretor:")
                st.markdown(response.text)
                
        except Exception as e:
            st.error(f"Ocorreu um erro durante a análise: {e}")