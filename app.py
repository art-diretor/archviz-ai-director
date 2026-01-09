import streamlit as st
import google.generativeai as genai
from PIL import Image
import os
from dotenv import load_dotenv

# 1. Configuração Inicial e Layout
st.set_page_config(page_title="ArchViz Director AI", page_icon="🏢", layout="wide")
load_dotenv()

# --- CSS para dar um tapa no visual (Opcional) ---
st.markdown("""
<style>
    .stButton>button {
        width: 100%;
        background-color: #FF4B4B;
        color: white;
        height: 3em;
        font-weight: bold;
    }
    .reportview-container {
        margin-top: -2em;
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
            st.warning("Por favor, insira sua API Key para começar.")
            st.stop()
    
    st.success("API Conectada!")
    st.info("Este app usa o Gemini 1.5 Flash para visão computacional.")

genai.configure(api_key=api_key)

# 3. Interface Principal
st.title("🏢 ArchViz AI Director")
st.markdown("### Gerador de Prompts para Detalhes (Freepik/Flux)")
st.write("Faça upload do seu render geral e receba prompts prontos para gerar os **Detail Shots**.")

uploaded_file = st.file_uploader("Arraste seu render ou croqui aqui", type=["jpg", "jpeg", "png"])

# 4. Lógica de Processamento
if uploaded_file is not None:
    image = Image.open(uploaded_file)
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.image(image, caption='Render Original', use_container_width=True)

    with col2:
        st.write("#### 🎯 Ação")
        generate_btn = st.button("Analisar e Gerar Prompts")

        if generate_btn:
            with st.spinner('O Diretor de Arte está analisando texturas e iluminação...'):
                try:
                    system_instruction = """
                    Atue como um Diretor de Fotografia Sênior especializado em Visualização Arquitetônica (ArchViz).
                    Analise a imagem fornecida. Sua missão é identificar 3 áreas da imagem que renderiam excelentes "Detail Shots" (Close-ups macro) para compor o portfólio.

                    Para cada uma das 3 áreas, escreva um PROMPT DE IMAGEM OTIMIZADO em INGLÊS para ser usado em geradores de IA (como Freepik Mystic, Flux ou Midjourney).

                    Regras de Ouro para os Prompts:
                    1. Use INGLÊS apenas.
                    2. Descreva a textura, o material e a iluminação em detalhes.
                    3. Inclua palavras-chave técnicas de fotografia: "Macro shot", "Extreme close-up", "Depth of field", "Bokeh", "8k resolution", "Photorealistic", "Soft cinematic lighting".
                    4. Não descreva a sala inteira, foque apenas no detalhe (ex: as fibras do tecido, o reflexo na madeira, a costura do couro).

                    Formato de Saída Obrigatório:
                    
                    ### 📸 Detalhe 1: [Nome do Elemento]
                    ```text
                    [Insira aqui o Prompt Completo em Inglês]
                    ```

                    ### 📸 Detalhe 2: [Nome do Elemento]
                    ```text
                    [Insira aqui o Prompt Completo em Inglês]
                    ```

                    ### 📸 Detalhe 3: [Nome do Elemento]
                    ```text
                    [Insira aqui o Prompt Completo em Inglês]
                    ```
                    """

                    model = genai.GenerativeModel('gemini-1.5-flash')
                    response = model.generate_content([system_instruction, image])
                    
                    st.success("Análise Concluída! Copie os prompts abaixo:")
                    st.markdown("---")
                    st.markdown(response.text)
                    
                except Exception as e:
                    st.error(f"Ocorreu um erro ao processar: {e}")

else:
    st.info("👈 Aguardando upload da imagem...")