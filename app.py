import streamlit as st
from groq import Groq
import PyPDF2

# --- 1. UI ARCHITECTURE ---
st.set_page_config(page_title="LEGACY V3 | Intelligence Agent", layout="wide", page_icon="💀")

st.markdown("""
<style>
    .block-container { max-width: 800px; padding-top: 1rem; }
    h1 { font-family: 'Courier New', Courier, monospace; letter-spacing: -2px; color: #E0E0E0; font-size: 3rem !important; }
    .stChatMessage { border-left: 4px solid #FF4B4B !important; background-color: #111111 !important; }
    code { color: #FF4B4B !important; }
</style>
""", unsafe_allow_html=True)

# --- 2. CORE ENGINE ---
if "GROQ_API_KEY" in st.secrets:
    api_key = st.secrets["GROQ_API_KEY"]
else:
    api_key = st.sidebar.text_input("🔑 AGENT_KEY", type="password")

if not api_key:
    st.info("Agent requires a valid key to initialize.")
    st.stop()

client = Groq(api_key=api_key)

# --- 3. PROFILING & EXTRACTION ---
def extract_engine(file):
    reader = PyPDF2.PdfReader(file)
    return "\n".join([p.extract_text() for p in reader.pages if p.extract_text()])

# --- 4. DATA INFUSION ---
with st.sidebar:
    st.title("📂 CORE DATA")
    file = st.file_uploader("Inject PDF", type="pdf")
    if file:
        if "data" not in st.session_state:
            st.session_state.data = extract_engine(file)
            st.success("DATA INFUSED.")
    else:
        st.session_state.data = ""

# --- 5. THE BEAST AGENT LOGIC ---
st.title("LEGACY V3.")

if "chat" not in st.session_state:
    st.session_state.chat = []

for m in st.session_state.chat:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

if p := st.chat_input("Berikan perintah bedah total..."):
    st.chat_message("user").markdown(p)
    st.session_state.chat.append({"role": "user", "content": p})

    # PROMPT INI DIBUAT UNTUK MENGHANCURKAN JAWABAN STANDAR
    intel_context = st.session_state.data[:25000] 
    
    beast_prompt = f"""
    PERSONALITY: Kamu adalah kritikus literatur paling sinis, cerdas, dan radikal. 
    TUGAS: Hancurkan teks ini dan bangun kembali dengan pemikiran baru. 
    DILARANG: Menggunakan kata 'membantu', 'meningkatkan', 'bermanfaat'. Gunakan bahasa teknis atau filosofis tinggi.

    ANALISIS WAJIB:
    1. **THE ANATOMY OF FAILURE**: Mengapa 99% orang yang membaca teks ini akan tetap gagal melakukan 'Deep Practice'? Bedah kesalahan interpretasi mereka.
    2. **THE MYELIN FALLACY**: Penulis bilang Myelin adalah kunci. Berikan argumen tandingan: Kapan Myelin justru menjadi 'penjara' bagi kreativitas?
    3. **UNSPOKEN TRUTH**: Berdasarkan teks Daud vs Goliat, bedah sisi gelap dari 'latihan': Apakah ini tentang kerja keras, atau tentang 'ketidaksengajaan yang dipaksakan'?
    4. **RADICAL EXECUTION**: Jangan beri saran 'berlatihlah'. Beri satu instruksi yang terasa menyakitkan tapi akan memberikan hasil instan.

    DATA SUMBER:
    {intel_context}
    """

    try:
        with st.chat_message("assistant"):
            res_box = st.empty()
            full = ""
            stream = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "system", "content": beast_prompt},
                          *[{"role": m["role"], "content": m["content"]} for m in st.session_state.chat]],
                temperature=0.7, # Menaikkan sedikit kreativitas agar tidak kaku
                stream=True,
            )
            for chunk in stream:
                if chunk.choices[0].delta.content:
                    full += chunk.choices[0].delta.content
                    res_box.markdown(full + "█")
            res_box.markdown(full)
            st.session_state.chat.append({"role": "assistant", "content": full})
    except Exception as e:
        st.error(f"FATAL: {e}")
