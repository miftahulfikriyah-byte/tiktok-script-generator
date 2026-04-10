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

# --- SISTEM LOGIN SEDERHANA ---
def check_password():
    """Mengembalikan True jika user memasukkan password yang benar."""
    def password_entered():
        # Anda bisa mengganti "RAHASIA123" dengan password pilihan Anda
        if st.session_state["password"] == "RAHASIA123": 
            st.session_state["password_correct"] = True
            del st.session_state["password"] # hapus password dari session agar aman
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        # Tampilan awal saat belum login
        st.title("🔐 Akses Terbatas")
        st.text_input(
            "Masukkan Password untuk Menggunakan Tool Ini:", 
            type="password", 
            on_change=password_entered, 
            key="password"
        )
        st.info("Aplikasi ini hanya untuk internal/pengguna khusus.")
        return False
    elif not st.session_state["password_correct"]:
        # Tampilan jika password salah
        st.text_input(
            "Password Salah! Coba lagi:", 
            type="password", 
            on_change=password_entered, 
            key="password"
        )
        st.error("😕 Akses ditolak.")
        return False
    else:
        return True

# JIKA PASSWORD BENAR, BARU JALANKAN APLIKASI UTAMA
if check_password():
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

    # --- FUNGSI UNTUK MENDAPATKAN MODEL YANG TERSEDIA SECARA OTOMATIS ---
    def get_working_model(api_key):
        genai.configure(api_key=api_key)
        try:
            # Mengambil daftar model yang mendukung pembuatan konten
            available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
            
            # Daftar prioritas model dari yang tercepat/terbaru
            priorities = [
                'models/gemini-1.5-flash-latest',
                'models/gemini-1.5-flash',
                'models/gemini-1.5-pro',
                'models/gemini-pro-vision'
            ]
            
            for p in priorities:
                if p in available_models:
                    return p
            
            # Jika tidak ada yang cocok, gunakan yang pertama tersedia
            return available_models[0] if available_models else 'gemini-1.5-flash'
        except Exception:
            # Fallback jika gagal melist model (biasanya masalah izin pada API Key tertentu)
            return 'gemini-1.5-flash'

    # --- FUNGSI API GEMINI UNTUK GENERATE SCRIPT ---
    def generate_scripts(api_key, main_img, aff_img, product_info):
        try:
            genai.configure(api_key=api_key)
            model_name = get_working_model(api_key)
            model = genai.GenerativeModel(model_name)
            
            prompt = f"""
            Bertindaklah sebagai Content Creator TikTok Affiliate profesional yang ahli membuat konten viral di Indonesia.
            
            Di hadapanmu ada dua gambar:
            1. Foto POV/Situasi (Kondisi sebelum ada produk).
            2. Foto Barang Shopee (Solusi atau produk yang dipromosikan).
            
            Informasi tambahan dari user: {product_info}
            
            Buatkan 3 variasi script iklan TikTok (Bahasa Indonesia Gaul/Relatable) yang menggabungkan kedua elemen tersebut secara cerdas:
            
            Variasi 1: "The Life Changer" (Bagaimana barang shopee ini mengubah situasi di foto pertama).
            Variasi 2: "Racun Shopee Check" (Kenapa penonton harus beli ini sekarang juga, fokus ke keunikan).
            Variasi 3: "POV Storytelling" (Cerita pendek penggunaan barang tersebut yang bikin relate).
            
            Struktur setiap script harus mencakup:
            - Hook (3 detik pertama) yang bikin orang berhenti scrolling.
            - Narasi Body (Penjelasan keunggulan produk).
            - Instruksi Visual (Footage apa yang harus direkam).
            - Call to Action (Ajak ke keranjang kuning atau link bio).
            
            Gunakan banyak emoji dan gaya bahasa anak muda (slang) seperti 'jujurly', 'parah sih', 'fix no debat'.
            """

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
    st.markdown("##### Buat Konten Viral dalam Hitungan Detik!")

    # Kotak Panduan
    st.markdown("""
    <div class="instruction-box">
        <strong>💡 CARA KERJA:</strong><br>
        1. Masukkan API Key di sidebar kiri.<br>
        2. Upload <b>Foto Situasi</b> dan <b>Foto Barang Shopee</b>.<br>
        3. Klik generate, dan AI akan meracik 3 ide script video sekaligus!
    </div>
    """, unsafe_allow_html=True)

    with st.sidebar:
        st.header("⚙️ Pengaturan")
        api_key = st.text_input("Google AI API Key:", type="password", help="Gunakan Gmail pribadi jika akun instansi bermasalah")
        st.divider()
        if st.button("Logout / Kunci Aplikasi"):
            st.session_state["password_correct"] = False
            st.rerun()

    # Area Input Gambar
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("1. Foto Situasi")
        main_file = st.file_uploader("Upload Foto Kondisi/POV", type=["jpg", "jpeg", "png"], key="main")

    with col2:
        st.subheader("2. Barang Shopee")
        aff_file = st.file_uploader("Upload Foto Produk Shopee", type=["jpg", "jpeg", "png"], key="aff")

    product_context = st.text_input("📝 Catatan Tambahan (Optional)", placeholder="Misal: Lagi promo 12.12, stok terbatas...")

    if main_file and aff_file:
        img1 = Image.open(main_file)
        img2 = Image.open(aff_file)
        
        st.divider()
        
        # Preview kedua gambar yang diupload
        pcol1, pcol2 = st.columns(2)
        with pcol1: st.image(img1, caption="Situasi Awal", use_container_width=True)
        with pcol2: st.image(img2, caption="Produk Shopee", use_container_width=True)

        if st.button("🚀 BUATKAN SCRIPT VIRAL! ✨"):
            if not api_key:
                st.warning("⚠️ Masukkan dulu API Key-nya di sidebar kiri ya!")
            else:
                with st.spinner("AI lagi mikir keras cari ide kreatif..."):
                    result = generate_scripts(api_key, img1, img2, product_context)
                    
                    if "Waduh" in result:
                        st.error(result)
                    else:
                        st.success("🔥 Script Berhasil Dibuat!")
                        st.markdown(result)
                        st.balloons()

    # Footer
    st.divider()
    st.caption("Akses Terbatas - Gunakan untuk kebutuhan Affiliate Anda")
