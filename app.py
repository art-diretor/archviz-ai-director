import streamlit as st
import google.generativeai as genai
from PIL import Image
import os
from dotenv import load_dotenv

# 1. Configuração Inicial
st.set_page_config(page_title="ArchViz AI Director", page_icon="🏢", layout="wide")
load_dotenv()

# CSS
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
    st.success("Conectado: Geração 2.5")

genai.configure(api_key=api_key)

# 3. Interface
st.title("🏢 ArchViz AI Director")
st.markdown("### Gerador de Prompts para Detalhes (Engine: Gemini 2.5)")

uploaded_file = st.file_uploader("Upload do Render", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    col1, col2 = st.columns([1, 1])
    image = Image.open(uploaded_file)
    
    with col1:
        st.image(image, caption='Original', use_container_width=True)

    with col2:
        st.write("#### 🎯 Ação")
        if st.button("Analisar e Gerar Prompts"):
            with st.spinner('Analisando composição e luz (Gemini 2.5)...'):
                
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

                # --- LÓGICA ATUALIZADA PARA SEUS MODELOS ---
                response = None
                
                # Lista de modelos baseada no seu diagnóstico
                # Tenta do mais novo para o mais antigo
                models_to_try = [
                    'gemini-2.5-flash',       # Tentativa 1: O mais novo
                    'gemini-2.0-flash',       # Tentativa 2: O estável da v2
                    'gemini-2.0-flash-exp',   # Tentativa 3: Experimental
                ]
                
                errors = []

                for model_name in models_to_try:
                    try:
                        # O SDK as vezes prefere sem o prefixo 'models/', mas se falhar, tentamos ajustar
                        model = genai.GenerativeModel(model_name)
                        response = model.generate_content([system_instruction, image])
                        if response:
                            break # Se funcionou, sai do loop
                    except Exception as e:
                        errors.append(f"{model_name}: {e}")
                        continue

                # Exibição
                if response:
                    st.success("Análise Concluída!")
                    st.markdown(response.text)
                else:
                    st.error("❌ Não foi possível gerar com os modelos disponíveis.")
                    with st.expander("Ver relatório de erros"):
                        st.write(errors)
                        st.info("Verifique se sua API Key tem acesso aos modelos da série 2.0/2.5")

else:
    st.info("👈 Faça o upload da imagem para começar.")