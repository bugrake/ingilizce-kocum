import streamlit as st
import google.generativeai as genai
import random
import string
import difflib

# 1. AYARLAR
st.set_page_config(page_title="AI İngilizce Koçu", layout="centered")

# 2. HAFIZA (SESSION STATE)
if 'skor' not in st.session_state: st.session_state.skor = 0
if 'soru' not in st.session_state: st.session_state.soru = None
if 'kelime_sorusu' not in st.session_state: st.session_state.kelime_sorusu = None
if 'cevap_verildi' not in st.session_state: st.session_state.cevap_verildi = False
if 'kelime_cevap_verildi' not in st.session_state: st.session_state.kelime_cevap_verildi = False
if 'ipucu_sayisi' not in st.session_state: st.session_state.ipucu_sayisi = 0

# 3. GEMINI BAĞLANTISI (DEĞİŞTİRİLEN KISIM BURASI)
try:
    if "GEMINI_KEY" in st.secrets:
        genai.configure(api_key=st.secrets["GEMINI_KEY"])
        
        # HATA ÇÖZÜMÜ: 'gemini-1.5-flash' yerine en güvenli liman olan 'gemini-pro'ya geçtik.
        # Bu model v1beta dahil her sürümde çalışır.
        model = genai.GenerativeModel('gemini-pro')
        
        ai_aktif = True
    else:
        st.error("❌ HATA: Secrets kısmında 'GEMINI_KEY' yok.")
        ai_aktif = False
except Exception as e:
    st.error(f"❌ BAĞLANTI HATASI: {type(e).__name__} - {str(e)}")
    ai_aktif = False

# 4. VERİTABANI
SENTENCES = {
    "A1": [
        {"eng": "My name is Sarah and I am twenty years old", "tr": "Adım Sarah ve yirmi yaşındayım"},
        {"eng": "There is a big table in the kitchen", "tr": "Mutfakta büyük bir masa var"},
        {"eng": "She usually wakes up at seven o'clock", "tr": "O genellikle saat yedide uyanır"},
        {"eng": "The cat is sleeping under the chair", "tr": "Kedi sandalyenin altında uyuyor"}
    ],
    "A2": [
        {"eng": "I visited my grandparents last summer", "tr": "Geçen yaz büyükanne ve büyükbabamı ziyaret ettim"},
        {"eng": "London is bigger than Manchester", "tr": "Londra Manchester'dan daha büyüktür"},
        {"eng": "I have never eaten sushi before", "tr": "Daha önce hiç suşi yemedim"}
    ],
    "B1": [
        {"eng": "If I win the lottery I will buy a house", "tr": "Piyangoyu kazanırsam bir ev alacağım"},
        {"eng": "This bridge was built by the Romans", "tr": "Bu köprü Romalılar tarafından inşa edildi"}
    ],
    "B2": [
        {"eng": "If I were you I would apologize to her immediately", "tr": "Senin yerinde olsam ondan hemen özür dilerdim"},
        {"eng": "I wish I had studied harder for the exam", "tr": "Keşke sınava daha sıkı çalışsaydım"}
    ]
}

KELIME_REHBERI = [
    {"w": "kitchen", "note": "💡 NOT: Oda isimlerinde 'in' kullanılır."},
    {"w": "airplane", "note": "💡 NOT: Hava taşıtlarında 'by' kullanılır."},
    {"w": "expensive", "note": "💡 NOT: 'Cheap' (Ucuz) kelimesinin zıttıdır."}
]

# 5. YARDIMCI FONKSİYONLAR
def temizle(metin):
    if not metin: return ""
    return metin.lower().strip().translate(str.maketrans('', '', string.punctuation))

def benzerlik_kontrol(tahmin, dogru):
    return difflib.SequenceMatcher(None, temizle(tahmin), temizle(dogru)).ratio()

def kelime_karistir(cumle):
    k = cumle.split()
    random.shuffle(k)
    return " / ".join(k)

def ai_analiz(tahmin, dogru, tr):
    if not ai_aktif: return "⚠️ AI şu an başlatılamadı."
    prompt = f"Sen bir İngilizce öğretmenisin. '{tr}' cümlesi için öğrenci '{tahmin}' dedi ama doğrusu '{dogru}'. Hatayı Türkçe ve kısa açıkla."
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"❌ AI HATASI: {type(e).__name__} - {str(e)}"

# 6. ARAYÜZ
st.sidebar.title("🤖 AI Koçu")
menu = st.sidebar.radio("Mod Seç:", ["Cümle Kurma", "Kelime Bilmecesi"])
st.sidebar.metric("🏆 Toplam Skor", st.session_state.skor)

# --- MOD 1: CÜMLE KURMA ---
if menu == "Cümle Kurma":
    st.header("📝 Cümle Kurma")
    seviye = st.selectbox("Seviye:", ["A1", "A2", "B1", "B2"])
    
    if st.button("Yeni Soru Getir", key="btn_yeni_soru"):
        st.session_state.soru = random.choice(SENTENCES[seviye])
        st.session_state.cevap_verildi = False
        st.session_state.ipucu_sayisi = 0
        st.rerun()

    if st.session_state.soru:
        soru = st.session_state.soru
        st.info(f"🇹🇷 **{soru['tr']}**")
        st.caption(f"Karışık: {kelime_karistir(soru['eng'])}")
        
        tahmin = st.text_input("İngilizcesini yazın:", key="inp_tahmin")
        
        c1, c2 = st.columns(2)
        
        if c1.button("Kontrol Et", key="btn_kontrol"):
            if not tahmin:
                st.warning("Cevap yazmadın!")
            else:
                oran = benzerlik_kontrol(tahmin, soru['eng'])
                if oran >= 0.85:
                    st.success(f"✅ DOĞRU! ({soru['eng']})")
                    if not st.session_state.cevap_verildi:
                        st.session_state.skor += 10
                        st.session_state.cevap_verildi = True
                        st.balloons()
                else:
                    st.error("🚫 Yanlış.")
                    with st.spinner("🤖 AI Öğretmen inceliyor..."):
                        analiz = ai_analiz(tahmin, soru['eng'], soru['tr'])
                        st.warning(f"**AI Notu:** {analiz}")

        if c2.button("İpucu", key="btn_ipucu"):
            st.session_state.ipucu_sayisi += 1
            kelimeler = soru['eng'].split()
            goster = " ".join(kelimeler[:st.session_state.ipucu_sayisi])
            st.write(f"💡 İpucu: **{goster}...**")

# --- MOD 2: KELİME BİLMECE ---
elif menu == "Kelime Bilmecesi":
    st.header("🧩 Kelime Bilmecesi")
    
    if st.button("Yeni Kelime", key="btn_yeni_kelime"):
        secilen = random.choice(KELIME_REHBERI)
        st.session_state.kelime_sorusu = secilen
        st.session_state.kelime_cevap_verildi = False
        st.rerun()
        
    if st.session_state.kelime_sorusu:
        soru_data = st.session_state.kelime_sorusu
        w_list = list(soru_data["w"])
        random.shuffle(w_list)
        karisik = "".join(w_list).upper()
        
        st.subheader(f"Harfler: {karisik}")
        st.write(f"İpucu: {soru_data['note']}")
        
        k_tahmin = st.text_input("Bu kelime nedir?", key="inp_kelime").lower().strip()
        
        if st.button("Tahmin Et", key="btn_kelime_kontrol"):
            if k_tahmin == soru_data["w"]:
                st.success(f"🎉 DOĞRU! {soru_data['w'].upper()}")
                if not st.session_state.kelime_cevap_verildi:
                    st.session_state.skor += 15
                    st.session_state.kelime_cevap_verildi = True
            else:
                st.error("❌ Yanlış.")
