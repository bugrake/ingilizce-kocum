import streamlit as st
import google.generativeai as genai
import random
import string
import difflib

# ==========================================
# 1. AYARLAR VE HAFIZA BAŞLATMA
# ==========================================
st.set_page_config(page_title="AI İngilizce Koçu", page_icon="🤖", layout="centered")

# Hafıza (Session State) değişkenlerini tek seferde kontrol ediyoruz
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

# ==========================================
# 2. GEMINI AI KURULUMU
# ==========================================
try:
    # Secrets panelinden anahtarı alıyoruz
    API_KEY = st.secrets["GEMINI_KEY"]
    genai.configure(api_key=API_KEY)
    
    # En güncel ve stabil model tanımlaması
    model = genai.GenerativeModel('gemini-1.5-flash')
    ai_aktif = True
except Exception as e:
    st.sidebar.error(f"AI Bağlantı Hatası: {e}")
    ai_aktif = False

# ==========================================
# 3. VERİTABANI
# ==========================================
SENTENCES = {
    "A1": [
        {"eng": "My name is Sarah and I am twenty years old", "tr": "Adım Sarah ve yirmi yaşındayım"},
        {"eng": "There is a big table in the kitchen", "tr": "Mutfakta büyük bir masa var"},
        {"eng": "The cat is sleeping under the chair", "tr": "Kedi sandalyenin altında uyuyor"}
    ],
    "A2": [
        {"eng": "London is bigger than Manchester", "tr": "Londra Manchester'dan daha büyüktür"},
        {"eng": "I have never eaten sushi before", "tr": "Daha önce hiç suşi yemedim"}
    ],
    "B1": [
        {"eng": "If I win the lottery I will buy a house", "tr": "Piyangoyu kazanırsam bir ev alacağım"},
        {"eng": "This bridge was built by the Romans", "tr": "Bu köprü Romalılar tarafından inşa edildi"}
    ],
    "B2": [
        {"eng": "I wish I had studied harder for the exam", "tr": "Keşke sınava daha sıkı çalışsaydım"},
        {"eng": "It is said that he is a millionaire", "tr": "Onun bir milyoner olduğu söyleniyor"}
    ]
}

GRAMMAR_TIPS = {
    "every": "💡 DERS NOTU: 'Every' (Her) geniş zaman ipucusudur.",
    "now": "💡 DERS NOTU: 'Now' (Şu an) şimdiki zamanı bildirir.",
    "if i": "💡 DERS NOTU: Koşul cümlesi (Conditional). Yapıya dikkat et."
}

KELIME_REHBERI = [
    {"w": "kitchen", "note": "💡 NOT: Oda isimlerinde 'in' kullanılır."},
    {"w": "breakfast", "note": "💡 NOT: Break (Kırmak) + Fast (Oruç)."}
]

# ==========================================
# 4. YARDIMCI FONKSİYONLAR
# ==========================================

def temizle(metin):
    if not metin: return ""
    metin = metin.lower().strip()
    kisaltmalar = {"i'm": "i am", "don't": "do not", "doesn't": "does not", "can't": "cannot"}
    for k, v in kisaltmalar.items(): metin = metin.replace(k, v)
    return metin.translate(str.maketrans('', '', string.punctuation))

def benzerlik_kontrol(tahmin, dogru):
    return difflib.SequenceMatcher(None, temizle(tahmin), temizle(dogru)).ratio()

def hata_vurgula(tahmin, dogru):
    t_kelimeler = tahmin.split()
    d_kelimeler = dogru.split()
    vurgulu = []
    for i, t in enumerate(t_kelimeler):
        if i < len(d_kelimeler) and benzerlik_kontrol(t, d_kelimeler[i]) > 0.8:
            vurgulu.append(f"<span style='color:green'>{t}</span>")
        else:
            vurgulu.append(f"<span style='color:red; text-decoration:line-through'>{t}</span>")
    return " ".join(vurgulu)

def ai_analiz(tahmin, dogru, tr):
    if not ai_aktif: return "⚠️ AI şu an aktif değil."
    prompt = f"Sen öğretmensin. '{tr}' cümlesi için öğrenci '{tahmin}' dedi ama doğrusu '{dogru}'. Hatayı Türkçe ve kısa açıkla."
    try:
        response = model.generate_content(prompt)
        return response.text
    except:
        return "🤖 AI şu an bir bağlantı sorunu yaşıyor."

# ==========================================
# 5. ARAYÜZ
# ==========================================

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
        
        tahmin = st.text_input("İngilizcesini yazın:", key="tahmin_input")
        
        col1, col2 = st.columns(2)
        
        if col1.button("Kontrol Et"):
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
                    st.markdown(f"**Detay:** {hata_vurgula(tahmin, soru['eng'])}", unsafe_allow_html=True)
                    with st.spinner("🤖 AI Öğretmen inceliyor..."):
                        analiz = ai_analiz(tahmin, soru['eng'], soru['tr'])
                        st.warning(f"**AI Notu:** {analiz}")

        if col2.button("İpucu (-2 Puan)"):
            st.session_state.ipucu_sayisi += 1
            st.write(f"💡 İpucu: {' '.join(soru['eng'].split()[:st.session_state.ipucu_sayisi])}...")

elif menu == "Kelime Bilmecesi":
    st.header("🧩 Kelime Bilmecesi")
    
    if st.button("Yeni Kelime"):
        secilen = random.choice(KELIME_REHBERI)
        w_list = list(secilen["w"])
        random.shuffle(w_list)
        st.session_state.kelime_sorusu = {
            "w": secilen["w"],
            "karisik": "".join(w_list).upper(),
            "note": secilen["note"]
        }
        st.session_state.kelime_cevap_verildi = False
        st.rerun()

    if st.session_state.kelime_sorusu:
        data = st.session_state.kelime_sorusu
        st.subheader(f"Harfler: {data['karisik']}")
        ktahmin = st.text_input("Tahmininiz:").lower().strip()
        
        if st.button("Kontrol Et"):
            if ktahmin == data["w"]:
                st.success(f"🎉 DOĞRU! {data['note']}")
                if not st.session_state.kelime_cevap_verildi:
                    st.session_state.skor += 15
                    st.session_state.kelime_cevap_verildi = True
            else:
                st.error("Tekrar dene!")
