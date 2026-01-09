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
    st.success("Conectado")
    
    # --- NOVO: Botão de Diagnóstico (Caso dê erro) ---
    st.markdown("---")
    if st.checkbox("🛠️ Ver Modelos Disponíveis"):
        try:
            genai.configure(api_key=api_key)
            st.write("Modelos que sua chave enxerga:")
            for m in genai.list_models():
                if 'generateContent' in m.supported_generation_methods:
                    st.code(m.name)
        except Exception as e:
            st.error(f"Erro ao listar: {e}")

genai.configure(api_key=api_key)

# 3. Interface
st.title("🏢 ArchViz AI Director")
st.markdown("### Gerador de Prompts para Detalhes")
st.info("💡 Dica: O uso é gratuito (Free Tier do Google AI Studio).")

uploaded_file = st.file_uploader("Upload do Render", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    col1, col2 = st.columns([1, 1])
    image = Image.open(uploaded_file)
    
    with col1:
        st.image(image, caption='Original', use_container_width=True)

    with col2:
        st.write("#### 🎯 Ação")
        if st.button("Analisar e Gerar Prompts"):
            with st.spinner('Analisando composição e luz...'):
                
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

                # --- LÓGICA ATUALIZADA (SÓ FAMÍLIA 1.5) ---
                response = None
                errors = []

                # Tenta Modelo 1: Flash (Rápido)
                try:
                    model = genai.GenerativeModel('gemini-1.5-flash')
                    response = model.generate_content([system_instruction, image])
                except Exception as e1:
                    errors.append(f"Flash falhou: {e1}")
                    
                    # Tenta Modelo 2: Pro (Mais robusto)
                    try:
                        st.warning("⚠️ Trocando para Gemini 1.5 Pro...")
                        model = genai.GenerativeModel('gemini-1.5-pro')
                        response = model.generate_content([system_instruction, image])
                    except Exception as e2:
                         errors.append(f"Pro falhou: {e2}")

                # Exibição
                if response:
                    st.success("Análise Concluída!")
                    st.markdown(response.text)
                else:
                    st.error("❌ Não foi possível gerar com nenhum modelo.")
                    with st.expander("Ver detalhes do erro"):
                        st.write(errors)
                        st.write("Dica: Use o checkbox na barra lateral para ver se sua API Key é válida.")

else:
    st.info("👈 Faça o upload da imagem para começar.")