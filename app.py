import streamlit as st
from groq import Groq
import PyPDF2

# --- 1. PREMIUM UI SETUP ---
st.set_page_config(page_title="LEGACY AI | Literary Intelligence", layout="wide", page_icon="🧬")

st.markdown("""
<style>
    /* Global Styles */
    .block-container { max-width: 900px; padding-top: 2rem; }
    h1 { background: linear-gradient(90deg, #00C9FF 0%, #92FE9D 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-weight: 800; letter-spacing: -1px; }
    .stChatMessage { border-radius: 15px; border: 1px solid #30363d; background-color: #0d1117; }
    
    /* Custom Sidebar */
    .css-1d391kg { background-color: #161b22; }
    
    /* Tooltip/Highlight style */
    .highlight { color: #92FE9D; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# --- 2. CORE ENGINE AUTHENTICATION ---
if "GROQ_API_KEY" in st.secrets:
    api_key = st.secrets["GROQ_API_KEY"]
else:
    api_key = st.sidebar.text_input("🧬 ACCESS TOKEN (GROQ KEY)", type="password")

if not api_key:
    st.info("⚡ System Offline: Harap masukkan Groq API Key di sidebar untuk menginisialisasi Agent.")
    st.stop()

client = Groq(api_key=api_key)

# --- 3. AGENTIC TOOLS (Enhanced PDF Processor) ---
def advanced_extraction(file):
    try:
        reader = PyPDF2.PdfReader(file)
        text_blocks = []
        for i, page in enumerate(reader.pages):
            content = page.extract_text()
            if content:
                text_blocks.append(f"[PAGE {i+1}]\n{content}")
        return "\n".join(text_blocks)
    except Exception as e:
        return f"Error critical pada sensor pembaca: {e}"

# --- 4. KNOWLEDGE REPOSITORY (Sidebar) ---
with st.sidebar:
    st.title("⚙️ AGENT CORE")
    st.markdown("---")
    uploaded_file = st.file_uploader("Suntikkan Data (PDF)", type="pdf")
    
    if uploaded_file:
        if "raw_intel" not in st.session_state or st.session_state.get("last_file") != uploaded_file.name:
            with st.status("Menganalisis Struktur Dokumen...", expanded=True) as status:
                st.write("Mengekstrak teks...")
                st.session_state.raw_intel = advanced_extraction(uploaded_file)
                st.session_state.last_file = uploaded_file.name
                status.update(label="Analisis Selesai!", state="complete", expanded=False)
            st.toast(f"Data {uploaded_file.name} berhasil diserap.", icon="✅")
    else:
        st.session_state.raw_intel = ""

# --- 5. THE ULTIMATE AGENT LOGIC ---
st.title("LEGACY: Literary Intelligence")

if "memory" not in st.session_state:
    st.session_state.memory = []

# Render Memory
for m in st.session_state.memory:
    with st.chat_message(m["role"], avatar=("🧬" if m["role"]=="assistant" else "👤")):
        st.markdown(m["content"])

# Agent Input
if user_query := st.chat_input("Berikan instruksi dekonstruksi..."):
    st.chat_message("user", avatar="👤").markdown(user_query)
    st.session_state.memory.append({"role": "user", "content": user_query})

    # PROMPT ENGINEERING: THE ARCHITECT PROMPT
    # Memaksa AI keluar dari zona nyaman Chatbot
    konteks_data = st.session_state.raw_intel[:20000] # Kapasitas ditingkatkan
    
    architect_prompt = f"""
    ROLE: Kamu adalah 'LEGACY', AI Agent penganalisis literatur tingkat tinggi dengan IQ 200.
    GAYA BICARA: Dingin, presisi, intelektual, dan provokatif. Jangan gunakan basa-basi pembuka.

    TUGAS DEKONSTRUKSI:
    Setiap kali User memberikan instruksi, kamu wajib membedah data menggunakan framework berikut:

    1. [SYNAPTIC CORE]: Temukan satu 'pola tersembunyi' atau paradoks dalam teks yang tidak disadari pembaca awam.
    2. [DEEP MECHANICS]: Jelaskan bagaimana mekanisme (seperti Myelin, Deep Practice, dll) bekerja secara brutal. Jangan jelaskan definisinya, jelaskan *cara kerjanya* terhadap kegagalan.
    3. [STRATEGIC FALLACY]: Apa kelemahan terbesar dari argumen penulis di bagian ini? Mengapa teori ini bisa gagal di dunia nyata?
    4. [THE 1% ACTION]: Berikan satu instruksi radikal yang harus dilakukan User sekarang juga untuk mendapatkan hasil 10x lipat berdasarkan teks ini.

    DOKUMEN SUMBER:
    {konteks_data if konteks_data else "Tidak ada dokumen. Gunakan pengetahuan internalmu tentang literatur dunia."}
    """

    try:
        with st.chat_message("assistant", avatar="🧬"):
            output_placeholder = st.empty()
            full_response = ""
            
            stream = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": architect_prompt},
                    *[{"role": m["role"], "content": m["content"]} for m in st.session_state.memory]
                ],
                temperature=0.2, # Meningkatkan presisi analisis
                stream=True,
            )

            for chunk in stream:
                if chunk.choices[0].delta.content:
                    full_response += chunk.choices[0].delta.content
                    output_placeholder.markdown(full_response + "▌")
            
            output_placeholder.markdown(full_response)
            st.session_state.memory.append({"role": "assistant", "content": full_response})

    except Exception as e:
        st.error(f"FATAL ERROR: {e}")
