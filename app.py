import streamlit as st
from groq import Groq
import PyPDF2

# --- 1. SETUP INTERFACE ---
st.set_page_config(page_title="AI Book Analyst Agent", layout="wide", page_icon="📚")

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
    st.info("Silakan masukkan Groq API Key di Sidebar untuk memulai.")
    st.stop()

client = Groq(api_key=api_key)

# --- 3. FUNGSI PEMBACA PDF ---
def ekstraksi_teks(file):
    try:
        reader = PyPDF2.PdfReader(file)
        full_text = ""
        for page in reader.pages:
            t = page.extract_text()
            if t: full_text += t
        return full_text
    except Exception as e:
        return f"Gagal membaca PDF: {e}"

# --- 4. SIDEBAR ---
with st.sidebar:
    st.title("📚 Agent Library")
    file_buku = st.file_uploader("Upload PDF Buku", type="pdf")
    if file_buku:
        if "konten_buku" not in st.session_state:
            with st.spinner("Agen sedang membaca buku..."):
                st.session_state.konten_buku = ekstraksi_teks(file_buku)
            st.success("Buku berhasil dianalisis!")
    else:
        st.session_state.konten_buku = ""

# --- 5. LOGIKA AI AGENT ---
st.title("AI Book Agent (Llama 3.3)")

if "obrolan" not in st.session_state:
    st.session_state.obrolan = []

# Tampilkan riwayat chat
for m in st.session_state.obrolan:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

# Aksi Chat
if prompt := st.chat_input("Apa yang ingin kamu bedah dari buku ini?"):
    st.chat_message("user").markdown(prompt)
    st.session_state.obrolan.append({"role": "user", "content": prompt})

    # Konteks (Max 15rb karakter)
    konteks = st.session_state.konten_buku[:15000] if st.session_state.konten_buku else "Tidak ada dokumen."

    try:
        with st.chat_message("assistant"):
            wadah_balasan = st.empty()
            teks_berjalan = ""
            
            # MENGGUNAKAN MODEL TERBARU: llama-3.3-70b-versatile
            stream = client.chat.completions.create(
                model="llama-3.3-70b-versatile", 
                messages=[
                    {"role": "system", "content": f"Kamu adalah AI Agent Analis Buku profesional. Analisis teks ini dengan tajam: {konteks}"},
                    *[{"role": m["role"], "content": m["content"]} for m in st.session_state.obrolan]
                ],
                stream=True,
            )

            for chunk in stream:
                if chunk.choices[0].delta.content:
                    teks_berjalan += chunk.choices[0].delta.content
                    wadah_balasan.markdown(teks_berjalan + "▌")
            
            wadah_balasan.markdown(teks_berjalan)
            st.session_state.obrolan.append({"role": "assistant", "content": teks_berjalan})

    except Exception as e:
        st.error(f"Error pada sistem Groq: {e}")
