import streamlit as st
import google.generativeai as genai
from PIL import Image
import time

# --- KONFIGURASI HALAMAN ---
st.set_page_config(
    page_title="TikTok Viral Script Generator",
    page_icon="🎬",
    layout="centered"
)

# --- CSS KUSTOM UNTUK TAMPILAN MODERN ---
st.markdown("""
    <style>
    .main {
        background-color: #f5f7f9;
    }
    .stButton>button {
        width: 100%;
        border-radius: 10px;
        height: 3em;
        background-color: #FE2C55;
        color: white;
        font-weight: bold;
        border: none;
    }
    .stButton>button:hover {
        background-color: #BD081C;
        color: white;
    }
    .instruction-box {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #FE2C55;
        margin-bottom: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- FUNGSI API GEMINI DENGAN RETRY LOGIC ---
def generate_scripts(api_key, image, product_info):
    genai.configure(api_key=api_key)
    
    # Menggunakan model Gemini 2.5 Flash yang sangat cepat dan gratis
    model = genai.GenerativeModel('gemini-2.5-flash-preview-09-2025')
    
    prompt = f"""
    Bertindaklah sebagai Content Creator TikTok dan Copywriter iklan profesional yang ahli membuat konten viral.
    
    Analisis foto produk yang dilampirkan. 
    Informasi tambahan dari user: {product_info}
    
    Buatkan 3 variasi script iklan TikTok dalam Bahasa Indonesia yang santai, kekinian (slang), dan persuasif.
    Setiap script harus memiliki struktur:
    1. Hook (3 detik pertama) - Harus sangat menarik perhatian.
    2. Body/Value Proposition - Jelaskan kenapa orang harus beli.
    3. Call to Action (CTA) - Arahkan untuk klik link atau keranjang kuning.
    
    Variasi 1: "The Problem-Solver" (Fokus ke masalah yang diselesaikan produk).
    Variasi 2: "The Aesthetic/Lifestyle" (Fokus ke keindahan dan gaya hidup).
    Variasi 3: "The Honest Review/POV" (Fokus seolah-olah review jujur pengguna).
    
    Gunakan gaya bahasa TikTok yang 'relatable' dan 'FYP-able'.
    """

    retries = 5
    for i in range(retries):
        try:
            response = model.generate_content([prompt, image])
            return response.text
        except Exception as e:
            if i < retries - 1:
                time.sleep(2 ** i)  # Jeda waktu sebelum mencoba lagi
                continue
            else:
                return f"Waduh, ada masalah koneksi API: {str(e)}"

# --- ANTARMUKA PENGGUNA (UI) ---
st.title("🎬 TikTok Viral Script Generator")

# Kotak Panduan Sederhana
with st.expander("🚀 CARA PAKAI (KLIK DI SINI)", expanded=False):
    st.markdown("""
    <div class="instruction-box">
    1. <b>Ambil API Key:</b> Buka <a href="https://aistudio.google.com/app/apikey" target="_blank">Google AI Studio</a> (Gratis).<br>
    2. <b>Input API Key:</b> Masukkan kodenya di kolom "Konfigurasi" di sebelah kiri (sidebar).<br>
    3. <b>Upload Foto:</b> Masukkan foto produk yang mau dipromosikan.<br>
    4. <b>Klik Generate:</b> Tunggu beberapa detik, script viralmu jadi!
    </div>
    """, unsafe_allow_html=True)

# Sidebar untuk input API Key
with st.sidebar:
    st.header("⚙️ Konfigurasi")
    api_key = st.text_input("Google AI API Key:", type="password", help="Dapatkan di Google AI Studio")
    st.divider()
    st.info("Aplikasi ini menggunakan Gemini 2.5 Flash untuk analisis gambar tingkat tinggi secara instan.")

# Area Input Utama
col1, col2 = st.columns([1, 1])

with col1:
    uploaded_file = st.file_uploader("📸 Upload Foto Produk", type=["jpg", "jpeg", "png"])

with col2:
    product_context = st.text_area("📝 Info Tambahan (Opsional)", 
                               placeholder="Contoh: Diskon 50%, khusus hari ini, atau target buat mahasiswa.",
                               height=125)

# Proses Generation
if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.divider()
    
    # Preview Image
    st.image(image, caption='Produk Kamu', use_container_width=True)

    if st.button("BUATKAN SCRIPT VIRAL! ✨"):
        if not api_key:
            st.warning("⚠️ Masukkan dulu API Key di sebelah kiri ya!")
        else:
            with st.spinner("Sabar ya, AI lagi mikir ide kreatif buat produkmu..."):
                result = generate_scripts(api_key, image, product_context)
                
                if "Waduh" in result:
                    st.error(result)
                else:
                    st.success("🔥 Mantap! Ini 3 variasi script buat kamu:")
                    st.markdown(result)
                    
                    st.info("💡 **Tips:** Kamu bisa langsung salin teks di atas ke Notepad atau langsung rekam videonya!")

# Footer
st.divider()
st.caption("Dibuat dengan ❤️ untuk UMKM Indonesia")
