import streamlit as st
import os
from dotenv import load_dotenv, set_key
from pathlib import Path
from PIL import Image
from utils.FileReaderChromaCreator import initChromaDB
from utils.FileReaderChromaCreator import process_new_uploaded
from utils.agent import gerarAnswer
import sys

def get_base_dir() -> Path:
    """Retorna o diretório onde estão os arquivos do app."""
    if getattr(sys, 'frozen', False):  # Rodando como executável (PyInstaller)
        return Path(sys.executable).parent
    else:  # Rodando via Python normal
        return Path(__file__).parent

exe_path = get_base_dir()

FILES_DIR = exe_path / "arquivos_ong"
FILES_DIR.mkdir(exist_ok=True)

DB_DIR = exe_path / "chroma_langchain_db"

img = Image.open((exe_path / "imagens" / "oikon_logo.png").as_posix())

ENV_PATH = (exe_path / ".env").as_posix()
load_dotenv(ENV_PATH)
api_key = os.getenv("OPENAI_API_KEY")

vector_store = initChromaDB(DB_DIR, FILES_DIR)

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
            load_dotenv(ENV_PATH, override=True)
            st.rerun()
        else:
            st.sidebar.error("❌ Chave inválida. Ela deve começar com 'sk-'.")
    st.stop()
else:
    new_api_key = st.sidebar.text_input(
        "Sua chave da OpenAI:",
        value=api_key,
        type="password"
    )

    if st.sidebar.button("Atualizar chave"):
        set_key(ENV_PATH, "OPENAI_API_KEY", new_api_key)
        load_dotenv(ENV_PATH, override=True)
        st.rerun()

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
    f for f in sorted((FILES_DIR / "processed").rglob("*"))
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

if uploaded_files:
    print(uploaded_files)
    for file in uploaded_files:
        file_path = FILES_DIR / "uploaded" / file.name
        with open(file_path, "wb") as f:
            f.write(file.getbuffer())

    st.sidebar.success("✅ Upload concluído com sucesso!")

    process_new_uploaded(FILES_DIR, vector_store)

selected_files = []

if filtered_files:
    st.sidebar.markdown("### 📁 Arquivos encontrados:")
    for f in filtered_files:
        # Cria um checkbox para cada arquivo
        checked = st.sidebar.checkbox(f"{file_icon(f.name)} {f.name}", key=f.name)
        if checked:
            selected_files.append(f)
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
        ans = gerarAnswer(prompt, 5, 0.4, vector_store)
        st.markdown(ans)