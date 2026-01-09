import streamlit as st
import google.generativeai as genai
from PIL import Image
import os
from dotenv import load_dotenv

# 1. Configuração Inicial
st.set_page_config(page_title="ArchViz Director AI", page_icon="🏢", layout="wide")
load_dotenv()

# CSS Opcional
st.markdown("""
<style>
    .stButton>button {
        width: 100%;
        background-color: #FF4B4B;
        color: white;
        height: 3em;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# 2. API Key
api_key = os.getenv("GOOGLE_API_KEY")

with st.sidebar:
    st.header("⚙️ Configurações")
    if not api_key:
        api_key = st.text_input("API Key:", type="password")
        if not api_key:
            st.warning("Insira a API Key.")
            st.stop()
    st.success("Conectado")

genai.configure(api_key=api_key)

# 3. Interface
st.title("🏢 ArchViz AI Director")
st.markdown("### Gerador de Prompts para Detalhes")

uploaded_file = st.file_uploader("Upload do Render", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    col1, col2 = st.columns([1, 1])
    image = Image.open(uploaded_file)
    
    with col1:
        st.image(image, caption='Original', use_container_width=True)

    with col2:
        st.write("#### 🎯 Ação")
        if st.button("Analisar e Gerar Prompts"):
            with st.spinner('Analisando...'):
                
                system_instruction = """
                Atue como um Diretor de Fotografia em ArchViz. Identifique 3 áreas para "Detail Shots".
                Para cada área, crie um PROMPT EM INGLÊS (focado em macro, textura e luz).
                Formato:
                ### 📸 Detalhe 1: [Nome]
                ```text
                [Prompt em Inglês]
                ```
                (Repita para 2 e 3)
                """

                # --- LÓGICA DE PROTEÇÃO (AQUI ESTÁ A CORREÇÃO) ---
                try:
                    # Tentativa 1: Tenta o modelo Flash (Rápido e Novo)
                    model = genai.GenerativeModel('gemini-1.5-flash-latest')
                    response = model.generate_content([system_instruction, image])
                
                except Exception as e:
                    # Tentativa 2: Se der erro (404), usa o modelo PRO VISION (Estável)
                    st.warning("⚠️ Modelo Flash indisponível. Usando backup (Gemini Pro Vision)...")
                    try:
                        model = genai.GenerativeModel('gemini-pro-vision')
                        response = model.generate_content([system_instruction, image])
                    except Exception as e2:
                        st.error(f"Erro fatal: {e2}")
                        st.stop()
                
                # Exibe o resultado
                st.success("Pronto! Copie abaixo:")
                st.markdown(response.text)