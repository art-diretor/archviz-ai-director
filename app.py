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

    /* Cards de Resultado */
    .prompt-box {
        background-color: #1a1c24;
        padding: 15px;
        border-radius: 6px;
        border-left: 4px solid #0078FF;
        margin-bottom: 15px;
    }
    
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
                "Foco extremo em materialidade e relevo (Lentes Macro)"
            ],
            label_visibility="collapsed"
        )
    
    with col_config2:
        st.markdown("### EXECUÇÃO")
        st.write(" ") 
        generate_btn = st.button("ANALISAR E GERAR PROMPTS")

    if generate_btn:
        st.markdown("---")
        
        progress_bar = st.progress(0)
        total_files = len(uploaded_files)
        
        for index, uploaded_file in enumerate(uploaded_files):
            image = Image.open(uploaded_file)
            
            st.markdown(f"### IMAGEM {index + 1}: {uploaded_file.name.upper()}")
            
            col_img, col_txt = st.columns([1, 1.5])
            
            with col_img:
                st.image(image, use_container_width=True)

            with col_txt:
                with st.spinner(f'Processando imagem {index + 1}...'):
                    
                    # INSTRUÇÃO PARA RETORNAR JSON (Muito mais organizado)
                    if mode == "MACRO TEXTURAS":
                        system_instruction = """
                        Role: Senior ArchViz Art Director.
                        Task: Identify 3 distinct areas for "Detail Shots" focused on MATERIALITY.
                        Visual Language: Macro lens, shallow depth of field, tactile textures, 8k resolution.
                        
                        You MUST return a JSON array with 3 objects. No other text.
                        Format:
                        [
                            {"title": "NAME OF ELEMENT", "reasoning": "Brief explanation of why this texture is interesting", "prompt": "The full english prompt here"},
                            {"title": "NAME OF ELEMENT", "reasoning": "...", "prompt": "..."}
                        ]
                        """
                    else: # CROPS DE COMPOSIÇÃO
                        system_instruction = """
                        Role: Senior ArchViz Art Director.
                        Task: Identify 3 distinct areas for "Composition Crops".
                        Visual Language: 35mm to 85mm lens. Focus on light, shadow, and furniture arrangement. 8k resolution.
                        
                        You MUST return a JSON array with 3 objects. No other text.
                        Format:
                        [
                            {"title": "NAME OF ELEMENT", "reasoning": "Brief explanation of composition", "prompt": "The full english prompt here"},
                            {"title": "NAME OF ELEMENT", "reasoning": "...", "prompt": "..."}
                        ]
                        """

                    response = None
                    models_to_try = ['gemini-2.5-flash', 'gemini-2.0-flash', 'gemini-1.5-pro']
                    
                    for model_name in models_to_try:
                        try:
                            model = genai.GenerativeModel(model_name)
                            # Forçamos JSON mode se o modelo suportar, ou confiamos no prompt
                            response = model.generate_content([system_instruction, image])
                            if response:
                                break 
                        except:
                            continue

                    if response:
                        try:
                            # Limpeza básica caso a IA coloque crases de markdown ```json ... ```
                            clean_text = response.text.replace("```json", "").replace("```", "").strip()
                            data = json.loads(clean_text)
                            
                            # RENDERIZAÇÃO ORGANIZADA
                            for item in data:
                                # Container visual customizado
                                st.markdown(f"""
                                <div style="margin-top: 10px; margin-bottom: 5px;">