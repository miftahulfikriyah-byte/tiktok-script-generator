import streamlit as st
import google.generativeai as genai
from PIL import Image
import time

# --- KONFIGURASI HALAMAN ---
st.set_page_config(
    page_title="TikTok Affiliate Script Generator",
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
        
        # Prioritas model 1.5 Flash karena paling stabil untuk analisis gambar
        priorities = [
            'models/gemini-1.5-flash-latest',
            'models/gemini-1.5-flash',
            'models/gemini-1.5-pro'
        ]
        
        for p in priorities:
            if p in available_models:
                return p
        
        return available_models[0] if available_models else 'gemini-1.5-flash'
    except Exception:
        return 'gemini-1.5-flash'

# --- FUNGSI API GEMINI UNTUK SCRIPT ---
def generate_scripts(api_key, main_img, aff_img, product_info):
    try:
        genai.configure(api_key=api_key)
        model_name = get_working_model(api_key)
        model = genai.GenerativeModel(model_name)
        
        prompt = f"""
        Bertindaklah sebagai Content Creator TikTok Affiliate profesional yang ahli membuat konten viral di Indonesia.
        
        Di hadapanmu ada dua gambar:
        1. Foto Produk Utama/Kondisi Pengguna (misal: orang lagi bosen, HP polos, kamar berantakan).
        2. Foto Barang Shopee yang akan dipromosikan (misal: casing HP lucu, lampu dekorasi, gadget unik).
        
        Informasi tambahan dari user: {product_info}
        
        Buatkan 3 variasi script iklan TikTok (Bahasa Indonesia Gaul/Relatable) yang menggabungkan kedua elemen tersebut:
        
        Variasi 1: "The Life Changer" (Bagaimana barang shopee ini mengubah situasi di foto pertama).
        Variasi 2: "Rekomendasi Racun" (Kenapa penonton harus beli ini sekarang juga).
        Variasi 3: "POV/Storytelling" (Cerita pendek penggunaan barang tersebut).
        
        Struktur setiap script:
        - Hook (3 detik pertama)
        - Body (Keunggulan & Visual yang harus diambil)
        - Call to Action (Ajak ke link bio/keranjang)
        
        Gunakan banyak emoji dan gaya bahasa anak muda.
        """

        # Memasukkan kedua gambar ke dalam list content
        response = model.generate_content(
            contents=[prompt, main_img, aff_img]
        )
        return response.text
    except Exception as e:
        if "API key not valid" in str(e):
            return "Waduh, API Key kamu salah. Cek lagi ya di Google AI Studio!"
        return f"Waduh, ada masalah koneksi API: {str(e)}"

# --- ANTARMUKA PENGGUNA (UI) ---
st.title("🎬 TikTok Affiliate AI Generator")
st.markdown("##### Racik Script Iklan Viral dari Foto Produk & Shopee!")

# Kotak Panduan
st.markdown("""
<div class="instruction-box">
    <strong>💡 CARA KERJA:</strong><br>
    Upload <b>Foto Utama</b> (kamu/situasi) dan <b>Foto Shopee</b>.<br>
    AI akan menganalisis keduanya untuk membuat script promosi yang nyambung!
</div>
""", unsafe_allow_html=True)

with st.sidebar:
    st.header("⚙️ Pengaturan")
    api_key = st.text_input("Google AI API Key:", type="password", help="Gunakan Gmail pribadi jika akun instansi bermasalah")
    st.divider()
    st.info("💡 Model yang digunakan: Gemini 1.5 Flash (Gratis & Stabil)")

# Area Input Gambar
col1, col2 = st.columns(2)

with col1:
    st.subheader("1. Foto Utama")
    main_file = st.file_uploader("Upload Foto Produk Utama/POV", type=["jpg", "jpeg", "png"], key="main")

with col2:
    st.subheader("2. Barang Shopee")
    aff_file = st.file_uploader("Upload Foto Barang Shopee", type=["jpg", "jpeg", "png"], key="aff")

product_context = st.text_input("📝 Catatan Tambahan (Optional)", placeholder="Misal: Lagi diskon flash sale, stok terbatas...")

if main_file and aff_file:
    img1 = Image.open(main_file)
    img2 = Image.open(aff_file)
    
    st.divider()
    
    # Preview kecil untuk kedua gambar
    pcol1, pcol2 = st.columns(2)
    with pcol1: st.image(img1, caption="Produk 1", use_container_width=True)
    with pcol2: st.image(img2, caption="Produk 2 (Shopee)", use_container_width=True)

    if st.button("BUATKAN SCRIPT VIRAL! ✨"):
        if not api_key:
            st.warning("⚠️ Masukkan dulu API Key-nya di sebelah kiri ya!")
        else:
            with st.spinner("AI lagi menganalisis kedua foto kamu..."):
                result = generate_scripts(api_key, img1, img2, product_context)
                
                if "Waduh" in result:
                    st.error(result)
                else:
                    st.success("🔥 Script Berhasil Dibuat!")
                    st.markdown(result)
                    st.balloons()

# Footer
st.divider()
st.caption("Gunakan script ini untuk ide konten CapCut atau langsung rekam di TikTok!")
