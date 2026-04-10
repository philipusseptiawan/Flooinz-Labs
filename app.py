import streamlit as st
from groq import Groq
import PyPDF2

# --- 1. SETUP UTAMA ---
st.set_page_config(page_title="Book Analyst Agent", layout="wide")

# Mengambil API Key (Prioritas: Secrets > Manual Input)
if "GROQ_API_KEY" in st.secrets:
    api_key = st.secrets["GROQ_API_KEY"]
else:
    api_key = st.sidebar.text_input("Groq API Key", type="password")

if not api_key:
    st.info("Masukkan Groq API Key di Sidebar untuk memulai.")
    st.stop()

client = Groq(api_key=api_key)

# --- 2. FUNGSI PEMBACA PDF ---
def baca_pdf(file):
    reader = PyPDF2.PdfReader(file)
    content = ""
    for page in reader.pages:
        txt = page.extract_text()
        if txt: content += txt
    return content

# --- 3. SIDEBAR (LOGIKA INPUT) ---
with st.sidebar:
    st.title("📚 Agent Library")
    file_buku = st.file_uploader("Unggah PDF Buku", type="pdf")
    
    if file_buku:
        if "isi_buku" not in st.session_state:
            with st.spinner("Agen sedang membaca..."):
                st.session_state.isi_buku = baca_pdf(file_buku)
            st.success("Buku dimuat!")
    else:
        st.session_state.isi_buku = ""

# --- 4. INTERFACE CHAT ---
st.title("✨ Book Summary Agent")

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

for pesan in st.session_state.chat_history:
    with st.chat_message(pesan["role"]):
        st.markdown(pesan["content"])

# --- 5. EKSEKUSI AGEN ---
if tanya := st.chat_input("Apa analisis kritis yang Anda butuhkan?"):
    st.chat_message("user").markdown(tanya)
    st.session_state.chat_history.append({"role": "user", "content": tanya})

    # Konteks Agen (Membatasi agar tidak overload)
    konteks = st.session_state.isi_buku[:12000] if st.session_state.isi_buku else "Belum ada buku."

    # Instruksi Agent (System Prompt)
    instruksi = f"""Kamu adalah AI Agent spesialis bedah buku. 
    Analisis teks berikut dengan kritis dan mendalam. 
    KONTEKS: {konteks}"""

    try:
        with st.chat_message("assistant"):
            box = st.empty()
            respon_lengkap = ""
            
            stream = client.chat.completions.create(
                model="llama3-70b-8192",
                messages=[
                    {"role": "system", "content": instruksi},
                    *[{"role": m["role"], "content": m["content"]} for m in st.session_state.chat_history]
                ],
                stream=True,
            )

            for chunk in stream:
                if chunk.choices[0].delta.content:
                    respon_lengkap += chunk.choices[0].delta.content
                    box.markdown(respon_lengkap + "▌")
            
            box.markdown(respon_lengkap)
            st.session_state.chat_history.append({"role": "assistant", "content": respon_lengkap})

    except Exception as e:
        st.error(f"Gagal memanggil Groq: {e}")
