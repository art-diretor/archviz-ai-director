import streamlit as st
import google.generativeai as genai
from PIL import Image
import os
import json
from dotenv import load_dotenv

# 1. Configuração da Página
st.set_page_config(page_title="KAAZA AI Director", page_icon="🟦", layout="wide")
load_dotenv()

# 2. DESIGN SYSTEM (Baseado no Brandbook Kaaza)
st.markdown("""
<style>
    /* Importando Fonte Montserrat do Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;600;700&display=swap');

    /* Aplicando a fonte em todo o app */
    html, body, [class*="css"] {
        font-family: 'Montserrat', sans-serif;
    }

    /* Títulos em Uppercase e Bold (Identidade Visual) */
    h1, h2, h3, h4 {
        font-weight: 700 !important;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    h1 { color: #FFFFFF; }
    h3 { color: #0078FF; } /* Kaaza Blue nos subtítulos */

    /* Estilização do Botão Principal */
    .stButton>button {
        width: 100%;
        background-color: #0078FF; /* Kaaza Blue */
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

    /* Estilização do File Uploader */
    [data-testid='stFileUploader'] {
        border: 1px dashed #464650; /* Urban Gray */
        border-radius: 4px;
        background-color: #001437; /* Midnight Blue bem sutil */
    }

    /* Estilização do Radio Button (Seletores) */
    .stRadio [role=radiogroup] {
        background-color: transparent;
    }
    
    /* Ajuste de Espaçamento */
    .block-container {
        padding-top: 3rem;
        padding-bottom: 3rem;
    }
    
    /* Sidebar mais discreta */
    section[data-testid="stSidebar"] {
        background-color: #0b0d12;
        border-right: 1px solid #1f2937;
    }
    
    /* Estilo para o Código */
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

# Upload de Múltiplos Arquivos
uploaded_files = st.file_uploader(
    "FAÇA O UPLOAD DOS RENDERS (MÁX 3)", 
    type=["jpg", "jpeg", "png"], 
    accept_multiple_files=True
)

if uploaded_files:
    # Aviso se o usuário subir mais de 3
    if len(uploaded_files) > 3:
        st.warning("Por favor, selecione no máximo 3 imagens por vez para melhor performance.")
        uploaded_files = uploaded_files[:3]

    st.markdown("---")
    
    # Seletor de Estilo
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
        st.write(" ") # Espaçamento
        generate_btn = st.button("ANALISAR E GERAR PROMPTS")

    # Lógica de Processamento
    if generate_btn:
        st.markdown("---")
        
        progress_bar = st.progress(0)
        total_files = len(uploaded_files)
        
        for index, uploaded_file in enumerate(uploaded_files):
            image = Image.open(uploaded_file)
            
            # Cabeçalho da Imagem
            st.markdown(f"### IMAGEM {index + 1}: {uploaded_file.name.upper()}")
            
            col_img, col_txt = st.columns([1, 1.5])
            
            with col_img:
                st.image(image, use_container_width=True)

            with col_txt:
                with st.spinner(f'Processando imagem {index + 1}...'):
                    
                    # --- AQUI ESTÁ A MUDANÇA: SOLICITANDO JSON ESTRUTURADO ---
                    if mode == "MACRO TEXTURAS":
                        system_instruction = """
                        Role: Senior ArchViz Art Director.
                        Task: Analyze the image and identify 3 distinct areas for "Detail Shots" focused on MATERIALITY.
                        Goal: Create prompts for Flux/Mystic to generate photorealistic close-ups.
                        Visual Language: Macro lens, shallow depth of field, tactile textures.
                        
                        IMPORTANT: You must return a pure JSON array (no markdown code blocks).
                        Structure:
                        [
                            {"title": "DETAIL NAME", "reasoning": "Why this texture matters...", "prompt": "Full English Prompt Here"},
                            {"title": "DETAIL NAME", "reasoning": "...", "prompt": "..."}
                        ]
                        """
                    else: # CROPS DE COMPOSIÇÃO
                        system_instruction = """
                        Role: Senior ArchViz Art Director.
                        Task: Analyze the image and identify 3 distinct areas for "Composition Crops".
                        Goal: Create prompts for Flux/Mystic to generate lifestyle vignettes or architectural details.
                        Visual Language: 35mm, 50mm or 85mm lens. Focus on light, shadow, and furniture arrangement. NO extreme macro.
                        
                        IMPORTANT: You must return a pure JSON array (no markdown code blocks).
                        Structure:
                        [
                            {"title": "CROP NAME", "reasoning": "Composition explanation...", "prompt": "Full English Prompt Here"},
                            {"title": "CROP NAME", "reasoning": "...", "prompt": "..."}
                        ]
                        """

                    response = None
                    models_to_try = ['gemini-2.5-flash', 'gemini-2.0-flash', 'gemini-1.5-pro']
                    
                    for model_name in models_to_try:
                        try:
                            model = genai.GenerativeModel(model_name)
                            response = model.generate_content([system_instruction, image])
                            if response:
                                break 
                        except:
                            continue

                    if response:
                        try:
                            # Limpeza da resposta para garantir JSON válido
                            clean_text = response.text.replace('```json', '').replace('```', '').strip()
                            data = json.loads(clean_text)
                            
                            # Renderização Organizada (Loop)
                            for item in data:
                                # Título e Explicação
                                st.markdown(f"""
                                <div style="margin-bottom: 5px; margin-top: 10px;">
                                    <span style="color: #0078FF; font-weight: bold; font-size: 1.1em;">// {item['title'].upper()}</span><br>
                                    <span style="color: #cccccc; font-size: 0.9em; font-style: italic;">{item['reasoning']}</span>
                                </div>
                                """, unsafe_allow_html=True)
                                
                                # Caixa de Código (Com botão de copiar nativo)
                                st.code(item['prompt'], language="text")
                                st.write("---")
                                
                        except Exception as e:
                            # Caso a IA falhe no JSON, mostra o texto bruto como fallback
                            st.warning("Formato simplificado (JSON falhou):")
                            st.write(response.text)
                    else:
                        st.error("Falha ao processar esta imagem.")
            
            st.markdown("---")
            progress_bar.progress((index + 1) / total_files)

else:
    st.info("Aguardando upload de arquivos para iniciar a direção de arte.")