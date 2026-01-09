import streamlit as st
import random
import string
import difflib
import time
import google.generativeai as genai

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="İngilizce Koçu", layout="centered")

# --- BURAYA EKLE: HAFIZA (SESSION STATE) BAŞLATMA ---
if 'skor' not in st.session_state: 
    st.session_state.skor = 0
if 'soru' not in st.session_state: 
    st.session_state.soru = None
if 'kelime_sorusu' not in st.session_state: 
    st.session_state.kelime_sorusu = None
if 'cevap_verildi' not in st.session_state: 
    st.session_state.cevap_verildi = False
if 'kelime_cevap_verildi' not in st.session_state: 
    st.session_state.kelime_cevap_verildi = False
if 'ipucu_sayisi' not in st.session_state: 
    st.session_state.ipucu_sayisi = 0
    
# ==========================================
# 1. AYARLAR VE GEMINI AI KURULUMU
# ==========================================
st.set_page_config(page_title="AI İngilizce Koçu", page_icon="🤖", layout="centered")

# --- BURAYA KENDİ API KEY'İNİ YAPIŞTIR ---
API_KEY = st.secrets["GEMINI_KEY"]  
# -----------------------------------------

try:
    genai.configure(api_key=API_KEY)
    model = genai.GenerativeModel('gemini-pro')
    ai_aktif = True
except:
    ai_aktif = False

# Session State (Hafıza)
if 'skor' not in st.session_state: st.session_state.skor = 0
if 'soru' not in st.session_state: st.session_state.soru = None
if 'cevap_verildi' not in st.session_state: st.session_state.cevap_verildi = False
if 'ipucu_sayisi' not in st.session_state: st.session_state.ipucu_sayisi = 0

# ==========================================
# 2. VERİTABANI (SENTENCES & KELIME_REHBERI)
# ==========================================
SENTENCES = {
    "A1": [
        {"eng": "My name is Sarah and I am twenty years old", "tr": "Adım Sarah ve yirmi yaşındayım"},
        {"eng": "There is a big table in the kitchen", "tr": "Mutfakta büyük bir masa var"},
        {"eng": "She usually wakes up at seven o'clock", "tr": "O genellikle saat yedide uyanır"},
        {"eng": "My father does not work on Sundays", "tr": "Babam pazar günleri çalışmaz"},
        {"eng": "They are playing football in the garden now", "tr": "Onlar şu an bahçede futbol oynuyorlar"},
        {"eng": "Where is the nearest bus station", "tr": "En yakın otobüs durağı nerede"},
        {"eng": "I have two brothers and one sister", "tr": "İki erkek ve bir kız kardeşim var"},
        {"eng": "This car is very expensive but beautiful", "tr": "Bu araba çok pahalı ama güzel"},
        {"eng": "The cat is sleeping under the chair", "tr": "Kedi sandalyenin altında uyuyor"},
        {"eng": "We go to the cinema every weekend", "tr": "Biz her hafta sonu sinemaya gideriz"},
        {"eng": "I drink milk every morning", "tr": "Her sabah süt içerim"},
        {"eng": "What time does the movie start", "tr": "Film saat kaçta başlıyor"}
    ],
    "A2": [
        {"eng": "I visited my grandparents last summer", "tr": "Geçen yaz büyükanne ve büyükbabamı ziyaret ettim"},
        {"eng": "She was cooking dinner when I arrived", "tr": "Ben geldiğimde o akşam yemeği pişiriyordu"},
        {"eng": "I think it will rain tomorrow afternoon", "tr": "Sanırım yarın öğleden sonra yağmur yağacak"},
        {"eng": "London is bigger than Manchester", "tr": "Londra Manchester'dan daha büyüktür"},
        {"eng": "You must wear a uniform at school", "tr": "Okulda üniforma giymelisin"},
        {"eng": "I have never eaten sushi before", "tr": "Daha önce hiç suşi yemedim"},
        {"eng": "We were not watching a movie last night", "tr": "Dün gece film izlemiyorduk"},
        {"eng": "I would like to order a cup of coffee", "tr": "Bir fincan kahve sipariş etmek istiyorum"}
    ],
    "B1": [
        {"eng": "If I win the lottery I will buy a house", "tr": "Piyangoyu kazanırsam bir ev alacağım"},
        {"eng": "This bridge was built by the Romans", "tr": "Bu köprü Romalılar tarafından inşa edildi"},
        {"eng": "I have been working here for ten years", "tr": "On yıldır burada çalışıyorum"},
        {"eng": "She asked me where I was going", "tr": "Bana nereye gittiğimi sordu"},
        {"eng": "The man who called yesterday is my boss", "tr": "Dün arayan adam benim patronum"},
        {"eng": "I used to play the guitar when I was young", "tr": "Gençken gitar çalardım"},
        {"eng": "You don't have to bring food", "tr": "Yiyecek getirmek zorunda değilsin"},
        {"eng": "It might be too late to catch the train", "tr": "Treni yakalamak için çok geç olabilir"}
    ],
    "B2": [
        {"eng": "If I were you I would apologize to her immediately", "tr": "Senin yerinde olsam ondan hemen özür dilerdim"},
        {"eng": "By the time we arrived the film had already started", "tr": "Biz vardığımızda film çoktan başlamıştı"},
        {"eng": "I wish I had studied harder for the exam", "tr": "Keşke sınava daha sıkı çalışsaydım"},
        {"eng": "Despite the heavy rain they continued the match", "tr": "Şiddetli yağmura rağmen maça devam ettiler"},
        {"eng": "You had better see a doctor before it gets worse", "tr": "Kötüleşmeden önce bir doktora görünsen iyi olur"},
        {"eng": "It is said that he is a millionaire", "tr": "Onun bir milyoner olduğu söyleniyor"},
        {"eng": "I regret not telling you the truth earlier", "tr": "Sana gerçeği daha önce söylemediğim için pişmanım"}
    ]
}

GRAMMAR_TIPS = {
    "every": "💡 DERS NOTU: 'Every' (Her) geniş zaman ipucusudur.",
    "now": "💡 DERS NOTU: 'Now' (Şu an) şimdiki zamanı (am/is/are + ing) bildirir.",
    "usually": "💡 DERS NOTU: Sıklık zarfları özne ile fiil arasına gelir.",
    "last": "💡 DERS NOTU: 'Last' geçmiş zaman (Simple Past) işaretidir.",
    "ago": "💡 DERS NOTU: 'Ago' (Önce) cümlenin sonunda kullanılır.",
    "if i": "💡 DERS NOTU: Koşul cümlesi (Conditional). Yapıya dikkat et.",
    "used to": "💡 DERS NOTU: Eskiden yapılan alışkanlıkları anlatır."
}

KELIME_REHBERI = [
    {"w": "kitchen", "note": "💡 NOT: Oda isimlerinde 'in' kullanılır."},
    {"w": "airplane", "note": "💡 NOT: Hava taşıtlarında 'by airplane' denir."},
    {"w": "doctor", "note": "💡 NOT: Mesleklerden önce 'a/an' gelir."},
    {"w": "thirsty", "note": "💡 NOT: 'Thirsty' (Susamak) ile 'Thirty' (30) karıştırma."},
    {"w": "beautiful", "note": "💡 NOT: 'Full' eki tek 'l' ile biter."},
    {"w": "expensive", "note": "💡 NOT: 'Cheap' (Ucuz) kelimesinin zıttıdır."},
    {"w": "breakfast", "note": "💡 NOT: Break (Kırmak) + Fast (Oruç)."}
]

# ==========================================
# 3. YARDIMCI FONKSİYONLAR
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

def kelime_karistir(cumle):
    k = cumle.split()
    random.shuffle(k)
    return " / ".join(k)

def ders_notu_getir(cumle):
    for k, v in GRAMMAR_TIPS.items():
        if k in cumle.lower(): return v
    return None

# --- YENİ: GEMINI AI ANALİZ FONKSİYONU ---
def ai_analiz(tahmin, dogru, tr):
    if not ai_aktif: return "⚠️ API Key girilmediği için AI çalışmıyor."
    
    prompt = f"""
    Sen yardımsever bir İngilizce öğretmenisin.
    Öğrenciye sorduğum Türkçe cümle: "{tr}"
    Doğru İngilizce çevirisi: "{dogru}"
    Öğrencinin verdiği hatalı cevap: "{tahmin}"
    
    Lütfen öğrenciye hatasını nazikçe açıkla. Gramer hatası mı yaptı, kelime mi unuttu? 
    Cevabın Türkçe olsun, kısa ve öğretici tut (maksimum 2-3 cümle).
    """
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"AI Bağlantı Hatası: {e}"

# ==========================================
# 4. ARAYÜZ (STREAMLIT)
# ==========================================

# Yan Menü
st.sidebar.image("https://img.freepik.com/free-vector/robot-teacher-concept-illustration_114360-1762.jpg", width=200)
st.sidebar.title("🤖 AI Koçu")
menu = st.sidebar.radio("Mod Seç:", ["Cümle Kurma", "Kelime Bilmecesi"])
st.sidebar.divider()
st.sidebar.metric("🏆 Toplam Skor", st.session_state.skor)

# --- MOD 1: CÜMLE KURMA ---
if menu == "Cümle Kurma":
    st.header("📝 Cümle Kurma Alıştırması")
    seviye = st.selectbox("Seviye:", ["A1", "A2", "B1", "B2"])
    
    if st.button("Yeni Soru Getir", type="primary"):
        st.session_state.soru = random.choice(SENTENCES[seviye])
        st.session_state.cevap_verildi = False
        st.session_state.ipucu_sayisi = 0
        st.rerun()

    if st.session_state.soru:
        soru = st.session_state.soru
        
        st.info(f"🇹🇷 **{soru['tr']}**")
        st.caption(f"Karışık Kelimeler: {kelime_karistir(soru['eng'])}")
        
        tahmin = st.text_input("İngilizcesini yazın:")
        
        c1, c2 = st.columns([1, 4])
        
        if c1.button("Kontrol Et"):
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
                    
                    notu = ders_notu_getir(soru['eng'])
                    if notu: st.info(notu)
                else:
                    st.error("🚫 Hatalı veya Eksik.")
                    st.markdown(f"**Detay:** {hata_vurgula(tahmin, soru['eng'])}", unsafe_allow_html=True)
                    
                    # --- AI BURADA DEVREYE GİRİYOR ---
                    with st.spinner("🤖 AI Öğretmen hatanı inceliyor..."):
                        analiz = ai_analiz(tahmin, soru['eng'], soru['tr'])
                        st.warning(f"**AI Öğretmen:** \n\n{analiz}")
                    # ---------------------------------

        if c2.button("İpucu (-2 Puan)"):
            st.session_state.ipucu_sayisi += 1
            kelimeler = soru['eng'].split()
            goster = " ".join(kelimeler[:st.session_state.ipucu_sayisi])
            st.write(f"💡 İpucu: **{goster}...**")
            if not st.session_state.cevap_verildi:
                st.session_state.skor -= 2

# --- MOD 2: KELİME BİLMECE ---
elif menu == "Kelime Bilmecesi":
    st.header("🧩 Kelime Bilmecesi")
    
    if st.button("Yeni Kelime Çek", type="primary"):
        secilen = random.choice(KELIME_REHBERI)
        kelime = secilen["w"]
        
        # Harf karıştırma
        w_list = list(kelime)
        random.shuffle(w_list)
        karisik_harfler = "".join(w_list).upper()
        
        # Boşluklu gösterme
        bosluklu = ""
        for char in kelime:
            if random.random() > 0.4:
                bosluklu += "_ "
            else:
                bosluklu += char.upper() + " "
                
        st.session_state.kelime_sorusu = {
            "w": kelime,
            "karisik": karisik_harfler,
            "bosluklu": bosluklu,
            "note": secilen["note"]
        }
        st.session_state.kelime_cevap_verildi = False
        st.rerun()
        
    if st.session_state.kelime_sorusu:
        soru_data = st.session_state.kelime_sorusu
        
        st.subheader(f"Karışık Harfler: {soru_data['karisik']}")
        st.write(f"İpucu: {soru_data['bosluklu']}")
        
        k_tahmin = st.text_input("Bu kelime nedir?").lower().strip()
        
        if st.button("Kelimeyi Kontrol Et"):
            if k_tahmin == soru_data["w"]:
                st.success(f"🎉 BİNGO! Doğru kelime: {soru_data['w'].upper()}")
                st.info(soru_data["note"])
                if not st.session_state.kelime_cevap_verildi:
                    st.session_state.skor += 15
                    st.session_state.kelime_cevap_verildi = True
                    st.balloons()
            else:
                st.error("❌ Yanlış, tekrar dene!")
