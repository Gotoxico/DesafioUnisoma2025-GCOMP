import streamlit as st
import os
from dotenv import load_dotenv, set_key
from pathlib import Path
from PIL import Image
from utils.FileReaderChromaCreator import carregarArquivo
from utils.FileReaderChromaCreator import initChromaDB
from utils.agent import gerarAnswer

img = Image.open("./imagens/oikon_logo.png")

# ===============================
# 🔐 Verificação e salvamento da chave da API
# ===============================
ENV_PATH = ".env"
load_dotenv(ENV_PATH)
api_key = os.getenv("OPENAI_API_KEY")

vector_stores = initChromaDB()


st.sidebar.markdown(
    '<h1 style="color:#F15A24;">🔐 Configuração da API</h1>',
    unsafe_allow_html=True
)

if not api_key:
    st.sidebar.warning("⚠️ Nenhuma chave da API foi encontrada.")
    api_key_input = st.sidebar.text_input(
        "Insira sua chave da OpenAI:",
        type="password",
        placeholder="sk-...",
    )

    if st.sidebar.button("Salvar chave"):
        if api_key_input.startswith("sk-"):
            set_key(ENV_PATH, "OPENAI_API_KEY", api_key_input)
            st.rerun()
        else:
            st.sidebar.error("❌ Chave inválida. Ela deve começar com 'sk-'.")
    st.stop()  # Impede o restante da interface até salvar a chave
else:
    # Permitir edição da chave
    new_api_key = st.sidebar.text_input(
        "Sua chave da OpenAI:",
        value=api_key,
        type="password"  # oculta os caracteres
    )

    if st.sidebar.button("Atualizar chave"):
        set_key(ENV_PATH, "OPENAI_API_KEY", new_api_key)
        st.rerun()

# ===============================
# 📂 Gerenciamento de arquivos
# ===============================

FILES_DIR = Path("./arquivos_ong/")
FILES_DIR.mkdir(exist_ok=True)

st.sidebar.markdown(
    '<h1 style="color:#F15A24;">📂 Arquivos conhecidos pelo agente</h1>',
    unsafe_allow_html=True
)

# Filtro por tipo
file_type_filter = st.sidebar.selectbox(
    "📑 Filtrar por tipo de arquivo:",
    ("Todos", "PDF (.pdf)", "Word (.docx)", "Texto (.txt)")
)

# Barra de pesquisa dinâmica
search_query = st.sidebar.text_input("🔍 Buscar arquivo por nome:")

# Extensões suportadas
supported_exts = {
    "Todos": [".pdf", ".docx", ".txt"],
    "PDF (.pdf)": [".pdf"],
    "Word (.docx)": [".docx"],
    "Texto (.txt)": [".txt"]
}

# 🔍 Buscar arquivos de forma recursiva
all_files = [
    f for f in sorted(FILES_DIR.rglob("*"))
    if f.is_file() and f.suffix.lower() in supported_exts[file_type_filter]
]

# Filtrar arquivos **em tempo real** conforme o usuário digita
filtered_files = [
    f for f in all_files if search_query.lower() in f.name.lower()
] if search_query else all_files

# Função para ícones conforme tipo
def file_icon(filename: str) -> str:
    ext = Path(filename).suffix.lower()
    if ext == ".pdf":
        return "📄"
    elif ext == ".docx":
        return "📝"
    elif ext == ".txt":
        return "📃"
    return "📦"

# Upload de arquivos (drag & drop)
uploaded_files = st.sidebar.file_uploader(
    "📤 Arraste e solte arquivos aqui ou clique para enviar",
    type=["pdf", "docx", "txt"],
    accept_multiple_files=True
)

if "upload_done" not in st.session_state:
    st.session_state.upload_done = False

if uploaded_files and not st.session_state.upload_done:
    for file in uploaded_files:
        file_path = FILES_DIR / file.name
        with open(file_path, "wb") as f:
            f.write(file.getbuffer())
        carregarArquivo(str(file_path.as_posix()), 0.01, vector_stores, True)

    st.sidebar.success("✅ Upload concluído com sucesso!")
    st.session_state.upload_done = True
    st.rerun()

# Após o rerun, limpar o estado para permitir novo upload
if st.session_state.upload_done:
    st.session_state.upload_done = False

# Exibir os arquivos filtrados na sidebar
if filtered_files:
    st.sidebar.markdown("### 📁 Arquivos encontrados:")
    for f in filtered_files:
        relative_path = f.relative_to(FILES_DIR)
        st.sidebar.markdown(f"- {file_icon(f.name)} **{relative_path}**")
else:
    st.sidebar.info("Nenhum arquivo encontrado.")

# Painel principal
with st.container(horizontal_alignment="center"):
    st.image(img)

st.markdown(
    '<h1 style="text-align: center;">💬 Pergunte ao modelo</h1>',
    unsafe_allow_html=True
)

prompt = st.chat_input("Digite sua pergunta:")
if prompt:
    with st.chat_message("user"):
        st.markdown(prompt)
    with st.chat_message("assistant"):
        ans = gerarAnswer(prompt, 5, 0.4, vector_stores)
        st.markdown(ans)