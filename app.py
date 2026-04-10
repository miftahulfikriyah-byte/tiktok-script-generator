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
        transition: 0.3s;
    }
    .stButton>button:hover {
        background-color: #BD081C;
        box-shadow: 0 4px 15px rgba(254, 44, 85, 0.3);
    }
    .instruction-box {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 12px;
        border-left: 6px solid #FE2C55;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        margin-bottom: 25px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- FUNGSI UNTUK MENDAPATKAN MODEL YANG TERSEDIA ---
def get_working_model(api_key):
    genai.configure(api_key=api_key)
    try:
        # Cek daftar model yang mendukung generateContent
        available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        
        # Prioritas model Flash karena paling cepat untuk gambar
        priorities = [
            'models/gemini-1.5-flash-latest',
            'models/gemini-1.5-flash',
            'models/gemini-pro-vision', # Fallback lama
            'models/gemini-1.5-pro'
        ]
        
        for p in priorities:
            if p in available_models:
                return p
        
        # Jika tidak ada yang cocok di prioritas, ambil yang pertama tersedia
        return available_models[0] if available_models else None
    except Exception:
        # Fallback manual jika list_models gagal (beberapa akun instansi membatasi ini)
        return 'gemini-1.5-flash'

# --- FUNGSI API GEMINI DENGAN PENGECEKAN MODEL ---
def generate_scripts(api_key, image, product_info):
    try:
        genai.configure(api_key=api_key)
        
        model_name = get_working_model(api_key)
        if not model_name:
            return "Waduh, akun API kamu tidak punya akses ke model Gemini manapun."
            
        model = genai.GenerativeModel(model_name)
        
        prompt = f"""
        Bertindaklah sebagai Content Creator TikTok dan Copywriter iklan profesional yang ahli membuat konten viral.
        
        Analisis foto produk yang dilampirkan secara detail. 
        Informasi tambahan dari user: {product_info}
        
        Buatkan 3 variasi script iklan TikTok dalam Bahasa Indonesia yang santai, kekinian (slang), dan persuasif.
        Setiap script harus memiliki struktur:
        1. Hook (3 detik pertama) - Harus sangat menarik perhatian (Attention Grabber).
        2. Body/Value Proposition - Jelaskan keunggulan produk.
        3. Call to Action (CTA) - Arahkan untuk klik link atau keranjang kuning.
        
        Variasi 1: "The Problem-Solver" (Fokus ke solusi masalah).
        Variasi 2: "The Aesthetic/Lifestyle" (Fokus ke vibe dan tren).
        Variasi 3: "The Honest Review/POV" (Seolah-olah testimoni jujur).
        
        Gunakan gaya bahasa TikTok Indonesia yang 'relatable'. Gunakan banyak emoji relevan.
        """

        retries = 3
        for i in range(retries):
            try:
                # Menggunakan parameter content yang lebih eksplisit
                response = model.generate_content(
                    contents=[prompt, image]
                )
                return response.text
            except Exception as e:
                if i < retries - 1:
                    time.sleep(2)
                    continue
                else:
                    raise e
                    
    except Exception as e:
        if "API key not valid" in str(e):
            return "Waduh, API Key kamu salah. Cek lagi ya di Google AI Studio!"
        return f"Waduh, ada masalah koneksi API: {str(e)}"

# --- ANTARMUKA PENGGUNA (UI) ---
st.title("🎬 TikTok Viral Script Generator")
st.markdown("##### Buat konten promosi yang auto-FYP dalam hitungan detik!")

# Kotak Panduan
st.markdown("""
<div class="instruction-box">
    <strong>💡 CARA MULAI:</strong><br>
    1. Masukkan API Key di menu <b>"Pengaturan"</b> di samping kiri.<br>
    2. Upload foto produk terbaikmu dan isi deskripsi singkat.<br>
    3. Klik tombol pink untuk generate script!
</div>
""", unsafe_allow_html=True)

# Sidebar untuk input API Key
with st.sidebar:
    st.header("⚙️ Pengaturan")
    api_key = st.text_input("Google AI API Key:", type="password", help="Dapatkan di Google AI Studio (Gratis)")
    st.divider()
    st.write("### Cara dapat API Key:")
    st.caption("1. Buka [Google AI Studio](https://aistudio.google.com/app/apikey)")
    st.caption("2. Login Google & Klik 'Create API Key'")
    st.caption("3. Copy dan Tempel di sini")
    st.info("Catatan: Jika pakai email kantor/instansi dan masih error, coba gunakan Gmail pribadi.")

# Area Input Utama
col1, col2 = st.columns([1, 1])

with col1:
    uploaded_file = st.file_uploader("📸 Upload Foto Produk", type=["jpg", "jpeg", "png"])

with col2:
    product_context = st.text_area("📝 Deskripsi Singkat", 
                               placeholder="Contoh: Sepatu putih, bahan kulit, diskon 50%",
                               height=125)

# Proses Generation
if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.divider()
    
    # Preview Image
    st.image(image, caption='Produk Terdeteksi', use_container_width=True)

    if st.button("BUATKAN SCRIPT VIRAL! ✨"):
        if not api_key:
            st.warning("⚠️ Masukkan dulu API Key-nya di sebelah kiri ya!")
        else:
            with st.spinner("AI lagi mikir ide kreatif..."):
                result = generate_scripts(api_key, image, product_context)
                
                if "Waduh" in result:
                    st.error(result)
                else:
                    st.success("🔥 Selesai! Copy script-nya di bawah ini:")
                    st.markdown(result)
                    st.balloons()

# Footer
st.divider()
st.caption("Tool Gratis untuk UMKM - Gunakan dengan Bijak")
