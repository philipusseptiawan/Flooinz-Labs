import streamlit as st
from groq import Groq
import PyPDF2

# --- 1. SETUP INTERFACE ---
st.set_page_config(page_title="Book Analyst Agent", layout="wide")

st.markdown("""
<style>
    .block-container { max-width: 850px; padding-top: 2rem; }
    .stChatInputContainer { position: fixed; bottom: 30px; }
    h1 { background: linear-gradient(45deg, #FF4B4B, #4527A0); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
</style>
""", unsafe_allow_html=True)

# --- 2. API KEY SETUP ---
if "GROQ_API_KEY" in st.secrets:
    api_key = st.secrets["GROQ_API_KEY"]
else:
    api_key = st.sidebar.text_input("Groq API Key", type="password")

if not api_key:
    st.info("Silakan masukkan Groq API Key di Sidebar.")
    st.stop()

client = Groq(api_key=api_key)

# --- 3. AGENT TOOLS (PDF READER) ---
def extrak_buku(file):
    reader = PyPDF2.PdfReader(file)
    content = ""
    for page in reader.pages:
        txt = page.extract_text()
        if txt: content += txt
    return content

# --- 4. SIDEBAR LIBRARY ---
with st.sidebar:
    st.title("📚 Agent Library")
    file = st.file_uploader("Upload PDF Buku", type="pdf")
    if file:
        if "data_buku" not in st.session_state:
            with st.spinner("Membaca isi buku..."):
                st.session_state.data_buku = extrak_buku(file)
            st.success("Buku Teranalisis!")
    else:
        st.session_state.data_buku = ""

# --- 5. LOGIKA AI AGENT ---
st.title("AI Book Agent")

if "history" not in st.session_state:
    st.session_state.history = []

for m in st.session_state.history:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

if prompt := st.chat_input("Apa yang ingin kamu bedah dari buku ini?"):
    st.chat_message("user").markdown(prompt)
    st.session_state.history.append({"role": "user", "content": prompt})

    # Konteks (Max 15rb karakter agar tidak limit)
    konteks = st.session_state.data_buku[:15000] if st.session_state.data_buku else "Tidak ada file."

    try:
        with st.chat_message("assistant"):
            box = st.empty()
            full_text = ""
            
            # MENGGUNAKAN MODEL TERBARU (Llama 3.1)
            stream = client.chat.completions.create(
                model="llama-3.1-70b-versatile", 
                messages=[
                    {"role": "system", "content": f"Kamu AI Agent Analis Buku. Bedah teks ini: {konteks}"},
                    *[{"role": m["role"], "content": m["content"]} for m in st.session_state.history]
                ],
                stream=True,
            )

            for chunk in stream:
                if chunk.choices[0].delta.content:
                    full_text += chunk.choices[0].delta.content
                    box.markdown(full_text + "▌")
            
            box.markdown(full_text)
            st.session_state.history.append({"role": "assistant", "content": full_text})

    except Exception as e:
        st.error(f"Gagal memanggil Groq: {e}")
