import streamlit as st
from groq import Groq
import PyPDF2

# --- 1. SETUP INTERFACE ---
st.set_page_config(page_title="AI Book Analyst Agent", layout="wide", page_icon="📝")

st.markdown("""
<style>
    .block-container { max-width: 850px; padding-top: 2rem; }
    .stChatInputContainer { position: fixed; bottom: 30px; }
    h1 { background: linear-gradient(45deg, #FF4B4B, #4527A0); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-size: 2.5rem !important; font-weight: 800; }
    .stChatMessage { border: 1px solid #f0f2f6; border-radius: 10px; padding: 10px; margin-bottom: 10px; }
</style>
""", unsafe_allow_html=True)

# --- 2. API KEY SETUP ---
if "GROQ_API_KEY" in st.secrets:
    api_key = st.secrets["GROQ_API_KEY"]
else:
    api_key = st.sidebar.text_input("🔑 Groq API Key", type="password", help="Masukkan API Key untuk mengaktifkan otak Agen.")

if not api_key:
    st.info("💡 Selamat datang! Silakan masukkan Groq API Key di Sidebar untuk memulai dekonstruksi buku.")
    st.stop()

client = Groq(api_key=api_key)

# --- 3. AGENT TOOLS (PDF ENGINE) ---
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

# --- 4. SIDEBAR LIBRARY ---
with st.sidebar:
    st.title("📚 Agent Library")
    file_buku = st.file_uploader("Upload PDF Buku", type="pdf")
    if file_buku:
        if "konten_buku" not in st.session_state or st.session_state.get("file_name") != file_buku.name:
            with st.spinner("Agen sedang membedah isi buku..."):
                st.session_state.konten_buku = ekstraksi_teks(file_buku)
                st.session_state.file_name = file_buku.name
            st.success("Analisis Awal Selesai!")
    else:
        st.session_state.konten_buku = ""

# --- 5. LOGIKA AI AGENT (ANALIS PROFESIONAL) ---
st.title("Literary Intelligence Agent")

if "obrolan" not in st.session_state:
    st.session_state.obrolan = []

# Tampilkan riwayat chat
for m in st.session_state.obrolan:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

# Aksi Chat
if prompt := st.chat_input("Berikan instruksi analisis (contoh: Bedah tesis utama buku ini)"):
    st.chat_message("user").markdown(prompt)
    st.session_state.obrolan.append({"role": "user", "content": prompt})

    # Batasi konteks agar tidak overload token (Llama 3.3 punya context window besar, tapi 15k aman untuk speed)
    konteks = st.session_state.konten_buku[:18000] if st.session_state.konten_buku else "Tidak ada dokumen yang diunggah."

    # AGENT PROMPT: Mengubah gaya chatbot menjadi Agen Analitis
    system_instruction = f"""
    Kamu adalah 'Senior Literary Intelligence Agent'. Tugasmu bukan merangkum teks secara pasif, 
    melainkan melakukan dekonstruksi intelektual. Gunakan nada bicara yang tajam, kritis, dan berwibawa.

    STRUKTUR RESPONS WAJIB:
    1. **The Core Thesis**: Satu kalimat kuat tentang argumen utama penulis.
    2. **Structural Pillars**: Analisis 3 konsep kunci yang membangun argumen tersebut.
    3. **Critical Synthesis**: Temukan celah logika, kontradiksi, atau wawasan yang jarang disadari.
    4. **Executive Implication**: Bagaimana pembaca bisa menerapkan teori ini secara konkret?

    DATA KONTEKS BUKU:
    {konteks}
    """

    try:
        with st.chat_message("assistant"):
            wadah_balasan = st.empty()
            teks_berjalan = ""
            
            stream = client.chat.completions.create(
                model="llama-3.3-70b-versatile", 
                messages=[
                    {"role": "system", "content": system_instruction},
                    *[{"role": m["role"], "content": m["content"]} for m in st.session_state.obrolan]
                ],
                temperature=0.4, # Sedikit kreatif tapi tetap faktual
                stream=True,
            )

            for chunk in stream:
                if chunk.choices[0].delta.content:
                    teks_berjalan += chunk.choices[0].delta.content
                    wadah_balasan.markdown(teks_berjalan + "▌")
            
            wadah_balasan.markdown(teks_berjalan)
            st.session_state.obrolan.append({"role": "assistant", "content": teks_berjalan})

    except Exception as e:
        st.error(f"Sistem Agen mengalami gangguan: {e}")
