import streamlit as st
import google.generativeai as genai
from PIL import Image
import os
from dotenv import load_dotenv

# 1. Configuração Inicial e Layout
st.set_page_config(page_title="ArchViz Director AI", page_icon="🏢", layout="wide")
load_dotenv()

# --- CSS para melhorar o botão ---
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

# 2. Configuração da API do Google
api_key = os.getenv("GOOGLE_API_KEY")

with st.sidebar:
    st.header("⚙️ Configurações")
    if not api_key:
        api_key = st.text_input("Cole sua Google API Key aqui:", type="password")
        if not api_key:
            st.warning("⚠️ Insira sua API Key para começar.")
            st.stop()
    
    st.success("API Conectada!")
    st.info("Modelo: Gemini 1.5 Flash")

# Configura a biblioteca
genai.configure(api_key=api_key)

# 3. Interface Principal
st.title("🏢 ArchViz AI Director")
st.markdown("### Gerador de Prompts para Detalhes (Freepik/Flux)")
st.write("Faça upload do seu render e receba prompts prontos para gerar **Detail Shots**.")

uploaded_file = st.file_uploader("Arraste seu render ou croqui aqui", type=["jpg", "jpeg", "png"])

# 4. Lógica de Processamento
if uploaded_file is not None:
    # Layout de colunas
    col1, col2 = st.columns([1, 1])
    
    image = Image.open(uploaded_file)
    
    with col1:
        st.image(image, caption='Render Original', use_container_width=True)

    with col2:
        st.write("#### 🎯 Ação")
        generate_btn = st.button("Analisar e Gerar Prompts")

        if generate_btn:
            with st.spinner('O Diretor de Arte está analisando a cena...'):
                try:
                    # PROMPT DO DIRETOR DE FOTOGRAFIA
                    system_instruction = """
                    Atue como um Diretor de Fotografia Sênior em ArchViz.
                    Analise a imagem. Identifique 3 áreas para "Detail Shots" (Close-ups macro).

                    Para cada área, crie um PROMPT DE IMAGEM em INGLÊS para geradores como Freepik Mystic ou Flux.

                    Regras:
                    1. Use APENAS INGLÊS nos prompts.
                    2. Foco em texturas, luz e realismo (8k, photorealistic, macro shot, depth of field).
                    3. Formate a saída exatamente assim:

                    ### 📸 Detalhe 1: [Nome]
                    ```text
                    [Prompt em Inglês]
                    ```

                    ### 📸 Detalhe 2: [Nome]
                    ```text
                    [Prompt em Inglês]
                    ```

                    ### 📸 Detalhe 3: [Nome]
                    ```text
                    [Prompt em Inglês]
                    ```
                    """

                    # Tenta carregar o modelo Flash
                    # Se der erro de nome, tente trocar para 'gemini-1.5-pro-latest'
                    model = genai.GenerativeModel('gemini-1.5-flash')
                    
                    response = model.generate_content([system_instruction, image])
                    
                    st.success("Análise Concluída! Copie os códigos abaixo:")
                    st.markdown(response.text)
                    
                except Exception as e:
                    st.error(f"Erro ao processar. Detalhes: {e}")
                    st.warning("Dica: Se o erro for 404, verifique se a API Key é válida e tem acesso ao modelo Flash.")

else:
    st.info("👈 Faça o upload da imagem para começar.")