import streamlit as st
import random
import difflib
import string

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="İngilizce Öğren", page_icon="🇬🇧")

# --- HAFIZA (SESSION STATE) ---
# Uygulama yenilendiğinde puanın ve sorunun kaybolmaması için
if 'skor' not in st.session_state:
    st.session_state.skor = 0
if 'soru_index' not in st.session_state:
    st.session_state.soru_index = 0

# --- VERİ SETİ (Buraya istediğin kadar ekleyebilirsin) ---
KELIME_REHBERI = [
    {"w": "kitchen", "note": "💡 NOT: Oda isimlerinde 'in' kullanılır."},
    {"w": "airplane", "note": "💡 NOT: Hava taşıtlarında 'by' kullanılır."},
    {"w": "breakfast", "note": "💡 NOT: Break (Kırmak) + Fast (Oruç)."}
]

# --- YARDIMCI FONKSİYONLAR ---
def temizle(metin):
    return metin.lower().strip().translate(str.maketrans('', '', string.punctuation))

# --- ANA ARAYÜZ ---
st.title("🎓 Mobil İngilizce Koçu")
st.sidebar.metric("Toplam Puan", st.session_state.skor)

mod = st.sidebar.selectbox("Bir Mod Seç", ["Ana Sayfa", "Kelime Bilmecesi"])

if mod == "Ana Sayfa":
    st.write("### Hoş Geldin! 👋")
    st.info("Sol menüden bir oyun seçerek İngilizce pratiğine başlayabilirsin.")
    st.write("Bu uygulama Streamlit ile mobil uyumlu hale getirilmiştir.")

elif mod == "Kelime Bilmecesi":
    st.subheader("🧩 Kelimeyi Tahmin Et!")
    
    # Yeni soru butonu
    if st.button("Yeni Soru Getir"):
        st.session_state.current_obj = random.choice(KELIME_REHBERI)
        # Harf karıştırma
        w = list(st.session_state.current_obj["w"])
        random.shuffle(w)
        st.session_state.karisik = "".join(w).upper()
        st.session_state.cevap_verildi = False

    if 'current_obj' in st.session_state:
        st.info(f"Karışık Harfler: **{st.session_state.karisik}**")
        tahmin = st.text_input("Tahminin nedir?").lower().strip()
        
        if st.button("Kontrol Et"):
            if tahmin == st.session_state.current_obj["w"]:
                st.success(f"🎉 DOĞRU! \n\n {st.session_state.current_obj['note']}")
                if not st.session_state.cevap_verildi:
                    st.session_state.skor += 15
                    st.session_state.cevap_verildi = True
                    st.balloons() # Ekranda balonlar uçar
            else:
                st.error("❌ Yanlış, tekrar dene!")
