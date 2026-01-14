import streamlit as st
import google.generativeai as genai
import random
import string
import difflib

# 1. Sayfa Ayarları (Hata almamak için en üstte olmalı)
st.set_page_config(page_title="AI İngilizce Koçu", page_icon="🤖", layout="centered")

# 2. Hafıza (Session State) Başlatma
keys = {
    'skor': 0,
    'soru': None,
    'kelime_sorusu': None,
    'cevap_verildi': False,
    'kelime_cevap_verildi': False,
    'ipucu_sayisi': 0
}
for key, value in keys.items():
    if key not in st.session_state:
        st.session_state[key] = value

# 3. Gemini Kurulumu
try:
    API_KEY = st.secrets["GEMINI_KEY"]
    genai.configure(api_key=API_KEY)
    # En stabil ve güncel model ismi
    model = genai.GenerativeModel('gemini-1.5-flash')
    ai_aktif = True
except Exception as e:
    st.sidebar.error(f"Bağlantı Hatası: {e}")
    ai_aktif = False

# 4. Veritabanı
SENTENCES = {
    "A1": [{"eng": "The cat is sleeping under the chair", "tr": "Kedi sandalyenin altında uyuyor"}],
    "A2": [{"eng": "I have never eaten sushi before", "tr": "Daha önce hiç suşi yemedim"}],
    "B1": [{"eng": "This bridge was built by the Romans", "tr": "Bu köprü Romalılar tarafından inşa edildi"}],
    "B2": [{"eng": "I wish I had studied harder for the exam", "tr": "Keşke sınava daha sıkı çalışsaydım"}]
}

# 5. Yardımcı Fonksiyonlar
def temizle(metin):
    if not metin: return ""
    return metin.lower().strip().translate(str.maketrans('', '', string.punctuation))

def benzerlik_kontrol(tahmin, dogru):
    return difflib.SequenceMatcher(None, temizle(tahmin), temizle(dogru)).ratio()

def ai_analiz(tahmin, dogru, tr):
    if not ai_aktif: return "⚠️ AI şu an aktif değil."
    prompt = f"Sen bir İngilizce öğretmenisin. '{tr}' cümlesi için öğrenci '{tahmin}' dedi ama doğrusu '{dogru}'. Hatayı Türkçe ve kısa açıkla."
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return "🤖 AI şu an bir bağlantı sorunu yaşıyor."

# 6. Arayüz
st.sidebar.title("🤖 AI Koçu")
menu = st.sidebar.radio("Mod Seç:", ["Cümle Kurma", "Kelime Bilmecesi"])
st.sidebar.metric("🏆 Toplam Skor", st.session_state.skor)

if menu == "Cümle Kurma":
    st.header("📝 Cümle Kurma Alıştırması")
    seviye = st.selectbox("Seviye Seç:", ["A1", "A2", "B1", "B2"])
    
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
