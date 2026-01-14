import streamlit as st
import google.generativeai as genai
import random
import string
import difflib

# 1. AYARLAR
st.set_page_config(page_title="AI İngilizce Koçu", layout="centered")

# 2. GEMINI BAĞLANTISI (Hatayı çözen kısım)
try:
    API_KEY = st.secrets["GEMINI_KEY"]
    genai.configure(api_key=API_KEY)
    # 404 hatasını önlemek için en güncel model ismi
    model = genai.GenerativeModel('gemini-1.5-flash')
    ai_aktif = True
except Exception as e:
    st.sidebar.error(f"Bağlantı Hatası: {e}")
    ai_aktif = False

# 3. HAFIZA (Session State)
if 'skor' not in st.session_state: st.session_state.skor = 0
if 'soru' not in st.session_state: st.session_state.soru = None
if 'cevap_verildi' not in st.session_state: st.session_state.cevap_verildi = False
if 'ipucu_sayisi' not in st.session_state: st.session_state.ipucu_sayisi = 0

# 4. VERİLER (Senin veritabanın)
SENTENCES = {
    "A1": [{"eng": "The cat is sleeping under the chair", "tr": "Kedi sandalyenin altında uyuyor"}],
    "A2": [{"eng": "I have never eaten sushi before", "tr": "Daha önce hiç suşi yemedim"}],
    "B1": [{"eng": "This bridge was built by the Romans", "tr": "Bu köprü Romalılar tarafından inşa edildi"}],
    "B2": [{"eng": "I wish I had studied harder for the exam", "tr": "Keşke sınava daha sıkı çalışsaydım"}]
}

# 5. YARDIMCI FONKSİYONLAR
def temizle(metin):
    return metin.lower().strip().translate(str.maketrans('', '', string.punctuation))

def benzerlik_kontrol(tahmin, dogru):
    return difflib.SequenceMatcher(None, temizle(tahmin), temizle(dogru)).ratio()

def ai_analiz(tahmin, dogru, tr):
    if not ai_aktif: 
        return "⚠️ AI Başlatılamadı. Lütfen Secrets ayarlarını ve internet bağlantısını kontrol edin."
    
    prompt = f"Sen bir İngilizce öğretmenisin. '{tr}' cümlesi için öğrenci '{tahmin}' dedi ama doğrusu '{dogru}'. Hatayı Türkçe ve kısa açıkla."
    
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        # HATAYI BURADA YAKALIYORUZ:
        # e.__class__.__name__ hatanın tipini (örn: InvalidArgument, PermissionDenied) verir.
        # str(e) ise Google'dan dönen detaylı hata mesajını verir.
        hata_mesaji = f"""
        ❌ AI Bağlantı Hatası Gerçekleşti!
        - Hata Tipi: {e.__class__.__name__}
        - Detaylı Mesaj: {str(e)}
        """
        return hata_mesaji

# Arayüzdeki hata gösterme kısmını da şöyle yapalım:
if st.button("Kontrol Et"):
    if tahmin:
        oran = benzerlik_kontrol(tahmin, soru['eng'])
        if oran < 0.85:
            st.error("🚫 Hatalı veya Eksik.")
            with st.spinner("🤖 AI Öğretmen hata kodlarını sorguluyor..."):
                analiz = ai_analiz(tahmin, soru['eng'], soru['tr'])
                # Eğer içinde "❌" varsa st.error ile, yoksa st.warning ile göster
                if "❌" in analiz:
                    st.error(analiz)
                else:
                    st.warning(f"**AI Notu:** {analiz}")
# 6. ARAYÜZ
st.sidebar.title("🤖 AI Koçu")
menu = st.sidebar.radio("Mod Seç:", ["Cümle Kurma", "Kelime Bilmecesi"])
st.sidebar.metric("🏆 Toplam Skor", st.session_state.skor)

if menu == "Cümle Kurma":
    st.header("📝 Cümle Kurma Alıştırması")
    seviye = st.selectbox("Seviye:", ["A1", "A2", "B1", "B2"])
    
    if st.button("Yeni Soru Getir"):
        st.session_state.soru = random.choice(SENTENCES[seviye])
        st.session_state.cevap_verildi = False
        st.session_state.ipucu_sayisi = 0
        st.rerun()

    if st.session_state.soru:
        soru = st.session_state.soru
        st.info(f"🇹🇷 **{soru['tr']}**")
        tahmin = st.text_input("İngilizcesini yazın:")
        
        if st.button("Kontrol Et"):
            if tahmin:
                oran = benzerlik_kontrol(tahmin, soru['eng'])
                if oran >= 0.85:
                    st.success(f"✅ HARİKA! ({soru['eng']})")
                    if not st.session_state.cevap_verildi:
                        st.session_state.skor += 10
                        st.session_state.cevap_verildi = True
                        st.balloons()
                else:
                    st.error("🚫 Hatalı veya Eksik.")
                    with st.spinner("🤖 AI Öğretmen inceliyor..."):
                        analiz = ai_analiz(tahmin, soru['eng'], soru['tr'])
                        st.warning(f"**AI Notu:** {analiz}")

# Kelime Bilmecesi modunu da buraya aynı mantıkla ekleyebilirsin.
