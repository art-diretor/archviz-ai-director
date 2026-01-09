import streamlit as st
import google.generativeai as genai
from PIL import Image
import os
import json
from dotenv import load_dotenv

# 1. Configuração da Página
st.set_page_config(page_title="KAAZA AI Director", page_icon="🟦", layout="wide")
load_dotenv()

# 2. DESIGN SYSTEM (Brandbook Kaaza)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Montserrat', sans-serif;
    }

    h1, h2, h3, h4 {
        font-weight: 700 !important;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    h1 { color: #FFFFFF; }
    h3 { color: #0078FF; }
    h4 { color: #A0A0A0; font-size: 0.9em; margin-bottom: 0px;}

    /* Botão Principal */
    .stButton>button {
        width: 100%;
        background-color: #0078FF;
        color: white;
        height: 3.5em;
        font-weight: 700;
        font-size: 14px;
        text-transform: uppercase;
        border-radius: 4px;
        border: none;
        transition: all 0.3s ease;
    }

    .stButton>button:hover {
        background-color: #005ecb;
        box-shadow: 0 4px 12px rgba(0, 120, 255, 0.3);
    }

    /* File Uploader */
    [data-testid='stFileUploader'] {
        border: 1px dashed #464650;
        border-radius: 4px;
        background-color: #001437;
    }

    /* Estilo do Código */
    .stCode {
        font-family: 'Courier New', monospace !important;
    }

</style>
""", unsafe_allow_html=True)

# 3. Configuração da API
api_key = os.getenv("GOOGLE_API_KEY")

with st.sidebar:
    st.markdown("### CONFIGURAÇÕES")
    if not api_key:
        api_key = st.text_input("API KEY", type="password")
        if not api_key:
            st.warning("Necessário inserir API Key.")
            st.stop()
    
    st.markdown("---")
    st.caption("SYSTEM STATUS: ONLINE")
    st.caption("ENGINE: GEMINI 2.5 FLASH")

genai.configure(api_key=api_key)

# 4. Interface Principal
st.title("KAAZA AI Director")
st.markdown("**GERE PROMPTS TÉCNICOS PARA VISUALIZAÇÃO ARQUITETÔNICA**")

uploaded_files = st.file_uploader(
    "FAÇA O UPLOAD DOS RENDERS (MÁX 3)", 
    type=["jpg", "jpeg", "png"], 
    accept_multiple_files=True
)

if uploaded_files:
    if len(uploaded_files) > 3:
        st.warning("Por favor, selecione no máximo 3 imagens por vez.")
        uploaded_files = uploaded_files[:3]

    st.markdown("---")
    
    col_config1, col_config2 = st.columns([1,1])
    with col_config1:
        st.markdown("### MODO DE ANÁLISE")
        mode = st.radio(
            "Selecione o objetivo:",
            ["CROPS DE COMPOSIÇÃO", "MACRO TEXTURAS"],
            captions=[
                "Foco em enquadramento, arquitetura e ambientação (Lentes 35mm-85mm)", 
                "Foco extremo em material