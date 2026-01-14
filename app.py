import streamlit as st
import google.generativeai as genai
import random
import string
import difflib

# ==========================================
# 1. AYARLAR VE HAFIZA
# ==========================================
st.set_page_config(page_title="Master AI İngilizce Koçu", layout="wide")

# Hafıza değişkenlerini başlat
for key, val in {
    'skor': 0, 'soru': None, 'cevap_verildi': False, 
    'kelime_bilmece': None
}.items():
    if key not in st.session_state: st.session_state[key] = val

# ==========================================
# 2. AI BAĞLANTISI (DOKUNULMADI - EN SAĞLAM HALİ)
# ==========================================
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

# ==========================================
# 3. AI ÜRETİM VE KONTROL MODÜLLERİ
# ==========================================

def ai_cumle_uret(seviye):
    """Veri tabanı yerine AI ile dinamik cümle üretir"""
    prompt = f"Bana {seviye} seviyesinde orta uzunlukta bir İngilizce cümle ve Türkçesini ver. Format sadece şu olsun: 'ingilizce|türkçe'. Örn: 'I am going home|Eve gidiyorum'."
    try:
        res = model.generate_content(prompt)
        raw = res.text.strip().replace('"', '').replace("*", "")
        if "|" in raw:
            eng, tr = raw.split("|")
            return {"eng": eng.strip(), "tr": tr.strip()}
    except:
        return {"eng": "Error generating sentence", "tr": "Cümle üretilemedi"}

def ai_cevap_kontrol_esnek(tahmin, dogru, tr):
    """TR -> ENG modunda devrik veya eş anlamlıları kabul eden kontrol"""
    if not ai_aktif: return None
    prompt = f"Türkçe: '{tr}'. Beklenen: '{dogru}'. Öğrenci: '{tahmin}'. Eğer anlam doğruysa (kelime sırası farklı olsa da) sadece 'OK' yaz. Yanlışsa Türkçe kısa açıklama yap."
    try:
        res = model.generate_content(prompt)
        return res.text.strip()
    except: return "AI şu an kontrol edemiyor."

def ai_kelime_bilmecesi_uret(seviye):
    """AI ile kelime bilmecesi üretme"""
    prompt = f"Bana {seviye} seviyesinde bir İngilizce kelime seç. Format: 'kelime|Türkçe karşılığı|İpucu'. Örn: 'sleep|uyumak|Night activity'."
    try:
        res = model.generate_content(prompt)
        return res.text.strip().replace("*", "")
    except: return "apple|elma|A red fruit"

# ==========================================
# 4. ARAYÜZ VE MODLAR
# ==========================================

st.sidebar.title("🤖 Master AI Koçu")
st.sidebar.info(f"Model: {target_model}")
st.sidebar.metric("🏆 Toplam Skor", st.session_state.skor)
mod = st.sidebar.radio("Oyun Modu Seç:", ["Çeviri (TR -> ENG)", "Karışık Kelimeler", "Cümle Kurma", "AI Kelime Bilmecesi"])

if st.sidebar.button("Skoru Sıfırla"): st.session_state.skor = 0; st.rerun()

# --- MOD 1: ÇEVİRİ (AI ÜRETİMLİ & AI KONTROLLÜ) ---
if mod == "Çeviri (TR -> ENG)":
    st.header("🌐 Türkçeden İngilizceye Çevir")
    seviye = st.selectbox("Seviye Seç:", ["A1", "A2", "B1", "B2", "C1"], key="tr_eng_sev")
    
    if st.button("Yeni Cümle Üret ✨", key="tr_eng_btn"):
        with st.spinner("AI cümle kuruyor..."):
            st.session_state.soru = ai_cumle_uret(seviye)
            st.session_state.cevap_verildi = False
            st.rerun()
    
    if st.session_state.soru:
        s = st.session_state.soru
        st.subheader(f"🇹🇷 {s['tr']}")
        tahmin = st.text_input("İngilizcesini yazın:", key="tr_eng_input")
        
        if st.button("Kontrol Et", key="tr_eng_check"):
            with st.spinner("AI analiz ediyor..."):
                sonuc = ai_cevap_kontrol_esnek(tahmin, s['eng'], s['tr'])
                if "OK" in sonuc.upper():
                    st.success(f"✅ Harika! Doğru kabul edildi.\nÖrnek cevap: {s['eng']}")
                    if not st.session_state.cevap_verildi:
                        st.session_state.skor += 20; st.session_state.cevap_verildi = True; st.balloons()
                else:
                    st.error(f"❌ Eksik veya hatalı!")
                    st.info(f"Öğretmen Notu: {sonuc}")

# --- MOD 2: KARIŞIK KELİMELER (AI ÜRETİMLİ) ---
elif mod == "Karışık Kelimeler":
    st.header("🔀 Kelimeleri Düzenle")
    seviye = st.selectbox("Seviye Seç:", ["A1", "A2", "B1", "B2", "C1"], key="mix_sev")
    
    if st.button("Yeni Soru Üret ✨", key="mix_btn"):
        with st.spinner("AI hazırlanıyor..."):
            st.session_state.soru = ai_cumle_uret(seviye)
            st.session_state.cevap_verildi = False
            st.rerun()
        
    if st.session_state.soru:
        s = st.session_state.soru
        words = s['eng'].split()
        random.shuffle(words)
        st.info(f"Kelimeler: {' / '.join(words)}")
        st.write(f"🇹🇷 Anlamı: {s['tr']}")
        
        tahmin = st.text_input("Doğru sıralamayı yazın:", key="mix_input")
        if st.button("Kontrol Et", key="mix_check"):
            if tahmin.lower().strip() == s['eng'].lower().strip():
                st.success("✅ Tam isabet!")
                if not st.session_state.cevap_verildi: st.session_state.skor += 10; st.session_state.cevap_verildi = True
            else:
                st.error(f"Yanlış! Doğrusu: {s['eng']}")

# --- MOD 3: CÜMLE KURMA (AI ÜRETİMLİ) ---
elif mod == "Cümle Kurma":
    st.header("📝 Bak ve Yaz")
    seviye = st.selectbox("Seviye Seç:", ["A1", "A2", "B1", "B2", "C1"], key="look_sev")
    if st.button("Yeni Soru Üret ✨", key="look_btn"):
        with st.spinner("AI hazırlanıyor..."):
            st.session_state.soru = ai_cumle_uret(seviye)
            st.session_state.cevap_verildi = False
            st.rerun()
    if st.session_state.soru:
        s = st.session_state.soru
        st.subheader(f"🇹🇷 {s['tr']}")
        st.write(f"🇬🇧 {s['eng']}")
        tahmin = st.text_input("Aynısını yazın:", key="look_input")
        if st.button("Kontrol Et", key="look_check"):
            if tahmin.strip() == s['eng']: st.success("✅ Başarılı!"); st.session_state.skor += 5
            else: st.error("Harf hatası yaptın!")

# --- MOD 4: AI KELİME BİLMECESİ ---
elif mod == "AI Kelime Bilmecesi":
    st.header("🧠 AI Kelime Bilmecesi")
    seviye = st.selectbox("Seviye:", ["A1", "A2", "B1", "B2", "C1"], key="riddle_sev")
    
    if st.button("AI'dan Kelime İste ✨", key="riddle_btn"):
        with st.spinner("AI kelime seçiyor..."):
            raw = ai_kelime_bilmecesi_uret(seviye)
            if "|" in raw:
                eng, tr, hint = raw.split("|")
                st.session_state.kelime_bilmece = {"eng": eng.strip(), "tr": tr.strip(), "hint": hint.strip()}
                st.session_state.cevap_verildi = False
                st.rerun()

    if st.session_state.kelime_bilmece:
        kb = st.session_state.kelime_bilmece
        st.info(f"💡 İpucu: {kb['hint']}")
        tahmin = st.text_input("Cevabınız (İngilizcesi veya Türkçesi):", key="riddle_input")
        
        if st.button("Tahmin Et", key="riddle_check"):
            t = tahmin.lower().strip()
            if t in kb['eng'].lower() or t in kb['tr'].lower():
                st.success(f"🎉 BİLDİN! {kb['eng']} = {kb['tr']}")
                if not st.session_state.cevap_verildi: st.session_state.skor += 25; st.session_state.cevap_verildi = True
            else:
                st.error("❌ Bilemedin, tekrar dene!")
