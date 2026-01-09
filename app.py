import streamlit as st
import google.generativeai as genai
from PIL import Image
import os
from dotenv import load_dotenv

# 1. Configuração Inicial
st.set_page_config(page_title="ArchViz AI Director", page_icon="🏢", layout="wide")
load_dotenv()

# CSS para estilização
st.markdown("""
<style>
    .stButton>button {
        width: 100%;
        background-color: #FF4B4B;
        color: white;
        height: 3em;
        font-weight: bold;
        border-radius: 8px;
    }
    .stRadio [role=radiogroup]{
        padding: 10px;
        background-color: #262730;
        border-radius: 8px;
    }
</style>
""", unsafe_allow_html=True)

# 2. API Key e Configuração
api_key = os.getenv("GOOGLE_API_KEY")

with st.sidebar:
    st.header("⚙️ Configurações")
    if not api_key:
        api_key = st.text_input("API Key:", type="password")
        if not api_key:
            st.warning("Insira a API Key.")
            st.stop()
    st.success("Conectado: Geração 2.5")

genai.configure(api_key=api_key)

# 3. Interface Principal
st.title("🏢 ArchViz AI Director")
st.markdown("### Gerador de Prompts para Detalhes")
st.write("Transforme seu render geral em prompts para gerar novos ângulos e detalhes.")

uploaded_file = st.file_uploader("Upload do Render", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    col1, col2 = st.columns([1, 1])
    image = Image.open(uploaded_file)
    
    with col1:
        st.image(image, caption='Render Original', use_container_width=True)

    with col2:
        st.write("#### 🎯 Configuração do Diretor")
        
        # --- SELETOR DE ESTILO ---
        mode = st.radio(
            "Qual o objetivo desses shots?",
            ["🖼️ Crops de Composição (Ambientação)", "🔍 Macro Texturas (Close-up)"],
            captions=["Foco em mobiliário, ângulos e arquitetura.", "Foco extremo em materiais, fibras e relevo."],
            horizontal=True
        )

        generate_btn = st.button("Analisar e Gerar Prompts")

        if generate_btn:
            with st.spinner(f'Criando prompts para {mode}...'):
                
                # --- DEFINIÇÃO DOS PROMPTS DO SISTEMA ---
                if mode == "🔍 Macro Texturas (Close-up)":
                    # Prompt focado em TEXTURA (O antigo)
                    system_instruction = """
                    Atue como um Diretor de Fotografia em ArchViz. Identifique 3 áreas para "Detail Shots" focados em MATERIALIDADE.
                    
                    Objetivo: Criar prompts para gerar imagens que mostrem a qualidade dos materiais (couro, madeira, tecido).
                    Linguagem visual: Macro lens, depth of field, texture focus.

                    Para cada área, crie um PROMPT EM INGLÊS.
                    Formato de Saída:
                    ### 📸 Macro 1: [Nome]
                    ```text
                    [Prompt em Inglês]
                    ```
                    (Repita para 2 e 3)
                    """
                else:
                    # Prompt focado em COMPOSIÇÃO (O novo)
                    system_instruction = """
                    Atue como um Diretor de Fotografia em ArchViz. Identifique 3 áreas para "Composition Crops" (Recortes de Composição).
                    
                    Objetivo: Criar prompts para gerar imagens que mostrem vinhetas de mobiliário, cantos arquitetônicos ou detalhes da fachada. 
                    NÃO USE MACRO EXTREMO. Use lentes 35mm, 50mm ou 85mm.
                    Foque na relação entre os objetos, luz e sombra, e design de interiores.
                    
                    Exemplos de foco: 
                    - "A cozy corner with the armchair and the floor lamp"
                    - "Geometric interaction between the ceiling beams and the wall"
                    - "Vertical composition of the brise-soleil"

                    Para cada área, crie um PROMPT EM INGLÊS.
                    Formato de Saída:
                    ### 🖼️ Crop 1: [Nome]
                    ```text
                    [Prompt em Inglês]
                    ```
                    (Repita para 2 e 3)
                    """

                # --- LÓGICA DE GERAÇÃO (Usando seus modelos 2.5/2.0) ---
                response = None
                models_to_try = ['gemini-2.5-flash', 'gemini-2.0-flash', 'gemini-2.0-flash-exp']
                errors = []

                for model_name in models_to_try:
                    try:
                        model = genai.GenerativeModel(model_name)
                        response = model.generate_content([system_instruction, image])
                        if response:
                            break 
                    except Exception as e:
                        errors.append(f"{model_name}: {e}")
                        continue

                # Exibição
                if response:
                    st.success("Análise Concluída!")
                    st.markdown(response.text)
                else:
                    st.error("Erro na geração.")
                    with st.expander("Ver erros"):
                        st.write(errors)

else:
    st.info("👈 Faça o upload da imagem para começar.")