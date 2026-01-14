import streamlit as st
import google.generativeai as genai
import random
import string
import difflib

# 1. AYARLAR
st.set_page_config(page_title="AI İngilizce Koçu", layout="centered")

# 2. HAFIZA BAŞLATMA
for key, val in {
    'skor': 0, 'soru': None, 'cevap_verildi': False, 
    'ipucu_sayisi': 0, 'kelime_sorusu': None
}.items():
    if key not in st.session_state: st.session_state[key] = val

# 3. GEMINI'YI ZORLA ÇALIŞTIRMA (HATA ÇÖZÜCÜ)
try:
    API_KEY = st.secrets["GEMINI_KEY"]
    genai.configure(api_key=API_KEY)
    
    # Mevcut modelleri listele ve en uygun olanı otomatik seç
    # Bu kısım 'v1beta' hatasını bypass eder
    available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
    
    # Tercih sırasına göre modeli seçiyoruz
    if 'models/gemini-1.5-flash' in available_models:
        target_model = 'gemini-1.5-flash'
    elif 'models/gemini-pro' in available_models:
        target_model = 'gemini-pro'
    else:
        target_model = available_models[0].replace('models/', '') # Bulduğun ilk çalışan modeli al

    model = genai.GenerativeModel(target_model)
    ai_aktif = True
    st.sidebar.success(f"Bağlı Model: {target_model}")
except Exception as e:
    st.sidebar.error(f"Kritik Bağlantı Hatası: {str(e)}")
    ai_aktif = False

# 4. VERİTABANI
SENTENCES = {
    "A1": [{"eng": "The cat is sleeping", "tr": "Kedi uyuyor"}],
    "A2": [{"eng": "I have a big house", "tr": "Büyük bir evim var"}],
    "B1": [{"eng": "This bridge was built in 1990", "tr": "Bu köprü 1990'da yapıldı"}],
    "B2": [{"eng": "I wish I had been there", "tr": "Keşke orada olsaydım"}]
}

# 5. FONKSİYONLAR
def ai_analiz(tahmin, dogru, tr):
    if not ai_aktif: return "❌ AI şu an devre dışı."
    prompt = f"İngilizce öğretmenisin. '{tr}' cümlesi için öğrenci '{tahmin}' dedi ama doğrusu '{dogru}'. Hatayı Türkçe ve kısa açıkla."
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"❌ ANALİZ HATASI: {str(e)}"

# 6. ARAYÜZ
st.title("🤖 İngilizce Koçu")
st.sidebar.metric("🏆 Skor", st.session_state.skor)

menu = st.sidebar.radio("Mod:", ["Cümle Kurma", "Kelime Oyunu"])

if menu == "Cümle Kurma":
    seviye = st.selectbox("Seviye:", ["A1", "A2", "B1", "B2"])
    
    if st.button("Yeni Soru", key="btn_new"):
        st.session_state.soru = random.choice(SENTENCES[seviye])
        st.session_state.cevap_verildi = False
        st.rerun()

    if st.session_state.soru:
        s = st.session_state.soru
        st.info(f"🇹🇷 {s['tr']}")
        tahmin = st.text_input("Çeviriniz:", key="user_input")
        
        if st.button("Kontrol Et", key="btn_check"):
            if tahmin:
                if difflib.SequenceMatcher(None, tahmin.lower().strip(), s['eng'].lower()).ratio() > 0.85:
                    st.success("✅ Doğru!")
                    if not st.session_state.cevap_verildi:
                        st.session_state.skor += 10
                        st.session_state.cevap_verildi = True
                        st.balloons()
                else:
                    st.error("🚫 Yanlış.")
                    with st.spinner("AI inceliyor..."):
                        st.warning(ai_analiz(tahmin, s['eng'], s['tr']))
