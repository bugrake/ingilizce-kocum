import streamlit as st
import google.generativeai as genai
import random
import string
import difflib

# ==========================================
# 1. AYARLAR VE HAFIZA (SESSION STATE)
# ==========================================
st.set_page_config(page_title="AI İngilizce Koçu", page_icon="🤖", layout="centered")

# Hafıza değişkenlerini güvenli bir şekilde başlatıyoruz
if 'skor' not in st.session_state: st.session_state.skor = 0
if 'soru' not in st.session_state: st.session_state.soru = None
if 'kelime_sorusu' not in st.session_state: st.session_state.kelime_sorusu = None
if 'cevap_verildi' not in st.session_state: st.session_state.cevap_verildi = False
if 'kelime_cevap_verildi' not in st.session_state: st.session_state.kelime_cevap_verildi = False
if 'ipucu_sayisi' not in st.session_state: st.session_state.ipucu_sayisi = 0

# ==========================================
# 2. GEMINI AI KURULUMU VE HATA YAKALAMA
# ==========================================
try:
    if "GEMINI_KEY" in st.secrets:
        genai.configure(api_key=st.secrets["GEMINI_KEY"])
        # En güncel model ismi. 404 hatasını önlemek için models/ ön eki kaldırıldı.
        model = genai.GenerativeModel('gemini-1.5-flash')
        ai_aktif = True
    else:
        st.error("❌ HATA: Streamlit Secrets kısmında 'GEMINI_KEY' bulunamadı.")
        ai_aktif = False
except Exception as e:
    st.error(f"❌ BAĞLANTI HATASI: {type(e).__name__} - {str(e)}")
    ai_aktif = False

# ==========================================
# 3. TÜM VERİTABANI (KISALTILMADI)
# ==========================================
SENTENCES = {
    "A1": [
        {"eng": "My name is Sarah and I am twenty years old", "tr": "Adım Sarah ve yirmi yaşındayım"},
        {"eng": "There is a big table in the kitchen", "tr": "Mutfakta büyük bir masa var"},
        {"eng": "She usually wakes up at seven o'clock", "tr": "O genellikle saat yedide uyanır"},
        {"eng": "My father does not work on Sundays", "tr": "Babam pazar günleri çalışmaz"},
        {"eng": "They are playing football in the garden now", "tr": "Onlar şu an bahçede futbol oynuyorlar"},
        {"eng": "Where is the nearest bus station", "tr": "En yakın otobüs durağı nerede"},
        {"eng": "The cat is sleeping under the chair", "tr": "Kedi sandalyenin altında uyuyor"}
    ],
    "A2": [
        {"eng": "I visited my grandparents last summer", "tr": "Geçen yaz büyükanne ve büyükbabamı ziyaret ettim"},
        {"eng": "London is bigger than Manchester", "tr": "Londra Manchester'dan daha büyüktür"},
        {"eng": "You must wear a uniform at school", "tr": "Okulda üniforma giymelisin"},
        {"eng": "I have never eaten sushi before", "tr": "Daha önce hiç suşi yemedim"}
    ],
    "B1": [
        {"eng": "If I win the lottery I will buy a house", "tr": "Piyangoyu kazanırsam bir ev alacağım"},
        {"eng": "This bridge was built by the Romans", "tr": "Bu köprü Romalılar tarafından inşa edildi"},
        {"eng": "I have been working here for ten years", "tr": "On yıldır burada çalışıyorum"}
    ],
    "B2": [
        {"eng": "If I were you I would apologize to her immediately", "tr": "Senin yerinde olsam ondan hemen özür dilerdim"},
        {"eng": "I wish I had studied harder for the exam", "tr": "Keşke sınava daha sıkı çalışsaydım"},
        {"eng": "It is said that he is a millionaire", "tr": "Onun bir milyoner olduğu söyleniyor"}
    ]
}

GRAMMAR_TIPS = {
    "every": "💡 DERS NOTU: 'Every' (Her) geniş zaman ipucusudur.",
    "now": "💡 DERS NOTU: 'Now' (Şu an) şimdiki zamanı bildirir.",
    "last": "💡 DERS NOTU: 'Last' geçmiş zaman (Simple Past) işaretidir."
}

KELIME_REHBERI = [
    {"w": "kitchen", "note": "💡 NOT: Oda isimlerinde 'in' kullanılır."},
    {"w": "airplane", "note": "💡 NOT: Hava taşıtlarında 'by' kullanılır."},
    {"w": "expensive", "note": "💡 NOT: 'Cheap' (Ucuz) kelimesinin zıttıdır."}
]

# ==========================================
# 4. YARDIMCI FONKSİYONLAR
# ==========================================
def temizle(metin):
    if not metin: return ""
    metin = metin.lower().strip()
    return metin.translate(str.maketrans('', '', string.punctuation))

def benzerlik_kontrol(tahmin, dogru):
    return difflib.SequenceMatcher(None, temizle(tahmin), temizle(dogru)).ratio()

def kelime_karistir(cumle):
    k = cumle.split()
    random.shuffle(k)
    return " / ".join(k)

# ANALİZ FONKSİYONU: HATA DETAYINI VEREN KISIM
def ai_analiz(tahmin, dogru, tr):
    if not ai_aktif: return "⚠️ AI şu an başlatılamadı."
    prompt = f"Sen bir İngilizce öğretmenisin. '{tr}' cümlesi için öğrenci '{tahmin}' dedi ama doğrusu '{dogru}'. Hatayı Türkçe ve kısa açıkla."
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        # Hata kodu ve detayını ekrana basıyoruz
        return f"❌ AI TEKNİK HATASI:\nTip: {type(e).__name__}\nDetay: {str(e)}"

# ==========================================
# 5. ARAYÜZ (MODLAR VE BUTONLAR)
# ==========================================
st.sidebar.title("🤖 AI Koçu")
menu = st.sidebar.radio("Mod Seç:", ["Cümle Kurma", "Kelime Bilmecesi"])
st.sidebar.divider()
st.sidebar.metric("🏆 Toplam Skor", st.session_state.skor)

# --- MOD 1: CÜMLE KURMA ---
if menu == "Cümle Kurma":
    st.header("📝 Cümle Kurma Alıştırması")
    seviye = st.selectbox("Seviye:", ["A1", "A2", "B1", "B2"])
    
    if st.button("Yeni Soru Getir", key="yeni_soru_btn"):
        st.session_state.soru = random.choice(SENTENCES[seviye])
        st.session_state.cevap_verildi = False
        st.session_state.ipucu_sayisi = 0
        st.rerun()

    if st.session_state.soru:
        soru = st.session_state.soru
        st.info(f"🇹🇷 **{soru['tr']}**")
        st.caption(f"Karışık Kelimeler: {kelime_karistir(soru['eng'])}")
        
        tahmin = st.text_input("İngilizcesini yazın:", key="tahmin_input")
        
        c1, c2 = st.columns(2)
        
        if c1.button("Kontrol Et", key="kontrol_btn"):
            if not tahmin:
                st.warning("Lütfen bir cevap yazın.")
            else:
                oran = benzerlik_kontrol(tahmin, soru['eng'])
                if oran >= 0.85:
                    st.success(f"✅ HARİKA! ({soru['eng']})")
                    if not st.session_state.cevap_verildi:
                        st.session_state.skor += 10
                        st.session_state.cevap_verildi = True
                        st.balloons()
                else:
                    st.error("🚫 Hatalı veya Eksik.")
                    with st.spinner("🤖 AI Öğretmen hatanı inceliyor..."):
                        analiz = ai_analiz(tahmin, soru['eng'], soru['tr'])
                        st.warning(f"**AI Analizi:**\n{analiz}")

        if c2.button("İpucu İste", key="ipucu_btn"):
            st.session_state.ipucu_sayisi += 1
            kelimeler = soru['eng'].split()
            goster = " ".join(kelimeler[:st.session_state.ipucu_sayisi])
            st.write(f"💡 İpucu: **{goster}...**")

# --- MOD 2: KELİME BİLMECE ---
elif menu == "Kelime Bilmecesi":
    st.header("🧩 Kelime Bilmecesi")
    
    if st.button("Yeni Kelime Çek", key="yeni_kelime_btn"):
        secilen = random.choice(KELIME_REHBERI)
        st.session_state.kelime_sorusu = secilen
        st.session_state.kelime_cevap_verildi = False
        st.rerun()
        
    if st.session_state.kelime_sorusu:
        soru_data = st.session_state.kelime_sorusu
        st.subheader(f"Kelime Bilmecesi İpucu: {soru_data['note']}")
        
        k_tahmin = st.text_input("Bu kelime nedir?", key="kelime_tahmin_input").lower().strip()
        
        if st.button("Kelimeyi Kontrol Et", key="kelime_kontrol_btn"):
            if k_tahmin == soru_data["w"]:
                st.success(f"🎉 BİNGO! Doğru kelime: {soru_data['w'].upper()}")
                if not st.session_state.kelime_cevap_verildi:
                    st.session_state.skor += 15
                    st.session_state.kelime_cevap_verildi = True
            else:
                st.error("❌ Yanlış, tekrar dene!")
