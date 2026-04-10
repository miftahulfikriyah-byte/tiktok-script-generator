import streamlit as st
import google.generativeai as genai
from PIL import Image
import time
import io
import base64

# --- KONFIGURASI HALAMAN ---
st.set_page_config(
    page_title="TikTok Affiliate AI Generator",
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
        available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        priorities = [
            'models/gemini-1.5-flash-latest',
            'models/gemini-1.5-flash',
            'models/gemini-1.5-pro'
        ]
        for p in priorities:
            if p in available_models:
                return p
        return available_models[0] if available_models else None
    except Exception:
        return 'gemini-1.5-flash'

# --- FUNGSI GENERATE GAMBAR GABUNGAN (AI Image Edit) ---
def generate_combined_image(api_key, main_img, affiliate_img):
    try:
        genai.configure(api_key=api_key)
        # Menggunakan model khusus image-to-image preview
        model = genai.GenerativeModel('gemini-2.5-flash-image-preview')
        
        prompt = "Gabungkan kedua produk ini ke dalam satu frame promosi TikTok yang estetik dan profesional. Buat pencahayaannya menyatu seolah-olah difoto bersamaan."
        
        response = model.generate_content(
            contents=[prompt, main_img, affiliate_img],
            generation_config={"response_modalities": ["IMAGE"]}
        )
        
        # Ekstrak data gambar dari response
        for part in response.candidates[0].content.parts:
            if part.inline_data:
                img_data = base64.b64decode(part.inline_data.data)
                return Image.open(io.BytesIO(img_data))
        return None
    except Exception as e:
        st.error(f"Gagal generate gambar gabungan: {str(e)}")
        return None

# --- FUNGSI API GEMINI UNTUK SCRIPT ---
def generate_scripts(api_key, main_img, aff_img, product_info):
    try:
        genai.configure(api_key=api_key)
        model_name = get_working_model(api_key)
        model = genai.GenerativeModel(model_name)
        
        prompt = f"""
        Bertindaklah sebagai Content Creator TikTok Affiliate profesional.
        Analisis foto produk utama dan foto barang shopee yang dilampirkan.
        
        Informasi tambahan: {product_info}
        
        Buatkan 3 variasi script TikTok viral yang mempromosikan barang shopee tersebut agar relevan digunakan dengan produk utama.
        
        Variasi 1: "Tips & Trick" (Cara pakai produk shopee ini bareng produk utama).
        Variasi 2: "Rekomendasi Murah" (Kenapa harus beli produk shopee ini).
        Variasi 3: "Aesthetic POV" (Vibe estetik penggunaan kedua barang).
        
        Sertakan juga instruksi gerakan/visual untuk setiap bagian video.
        Gunakan gaya bahasa gaul TikTok Indonesia dan emoji.
        """

        response = model.generate_content(
            contents=[prompt, main_img, aff_img]
        )
        return response.text
    except Exception as e:
        return f"Masalah API: {str(e)}"

# --- ANTARMUKA PENGGUNA (UI) ---
st.title("🎬 TikTok Affiliate AI Generator")
st.markdown("##### Gabung Produk + Barang Shopee jadi Konten Viral!")

with st.sidebar:
    st.header("⚙️ Pengaturan")
    api_key = st.text_input("Google AI API Key:", type="password")
    st.divider()
    st.info("💡 Gunakan Gmail pribadi jika akun instansi membatasi akses API.")

# Area Input Gambar
col1, col2 = st.columns(2)

with col1:
    st.subheader("1. Produk Utama")
    main_file = st.file_uploader("Upload Foto Kamu/Produk Utama", type=["jpg", "png"], key="main")

with col2:
    st.subheader("2. Barang Shopee")
    aff_file = st.file_uploader("Upload Screenshot Barang Shopee", type=["jpg", "png"], key="aff")

product_context = st.text_input("📝 Catatan Tambahan (Optional)", placeholder="Misal: Spil link di bio, harga cuma 10rb...")

if main_file and aff_file:
    img1 = Image.open(main_file)
    img2 = Image.open(aff_file)
    
    st.divider()
    
    if st.button("🚀 GENERATE KONTEN GABUNGAN ✨"):
        if not api_key:
            st.warning("⚠️ Masukkan API Key dulu di samping!")
        else:
            # Tahap 1: Generate Gambar Gabungan AI
            with st.spinner("Menggabungkan produk dengan AI..."):
                combined_img = generate_combined_image(api_key, img1, img2)
                
                if combined_img:
                    st.success("📸 Visual Gabungan AI Berhasil Dibuat!")
                    st.image(combined_img, use_container_width=True)
                    
                    # Tahap 2: Generate Script Iklan
                    with st.spinner("Meracik script viral..."):
                        script_result = generate_scripts(api_key, img1, img2, product_context)
                        st.divider()
                        st.markdown("### 📝 Script TikTok Anda")
                        st.markdown(script_result)
                        st.balloons()
                else:
                    st.error("Gagal menggabungkan gambar. Pastikan API Key mendukung Gemini 2.5 Image Preview.")

# Footer
st.divider()
st.caption("Gunakan visual AI sebagai referensi editing video TikTok Anda!")
