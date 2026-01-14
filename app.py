import streamlit as st
import google.generativeai as genai
import random
import string
import difflib
import json
import os
import pandas as pd

# ==========================================
# 1. GÜVENLİK AYARLARI (BURAYI KENDİNE GÖRE DÜZENLE)
# ==========================================
VALID_PASSKEYS = ["KRALINYO2024", "AI_PRO_99", "VIP_ACCESS", "anan"] # Geçiş anahtarların
IP_WHITELIST = ["127.0.0.1", "123.456.78.90", "192.168.0.102", "192.168.15.213", "192.168.0.48"] 

# Kullanıcının gerçek IP adresini alma fonksiyonu
def get_remote_ip():
    try:
        from streamlit.web.server.websocket_headers import _get_websocket_headers
        headers = _get_websocket_headers()
        if headers:
            return headers.get("X-Forwarded-For", "Bilinmiyor").split(",")[0]
    except:
        return "Bilinmiyor"
    return "Bilinmiyor"

# ==========================================
# 2. AYARLAR VE HAFIZA
# ==========================================
st.set_page_config(page_title="VIP AI Dil Koçu", layout="wide", page_icon="🌍")

if 'auth' not in st.session_state: st.session_state['auth'] = False
if 'skor' not in st.session_state: st.session_state['skor'] = 0
if 'soru' not in st.session_state: st.session_state['soru'] = None
if 'cevap_verildi' not in st.session_state: st.session_state['cevap_verildi'] = False
if 'kelime_bilmece' not in st.session_state: st.session_state['kelime_bilmece'] = None # Hata almamak için eklendi

# ==========================================
# 3. AI BAĞLANTISI
# ==========================================
try:
    API_KEY = st.secrets["GEMINI_KEY"]
    genai.configure(api_key=API_KEY)
    
    available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
    
    if 'models/gemini-1.5-flash' in available_models:
        target_model = 'gemini-1.5-flash'
    elif 'models/gemini-pro' in available_models:
        target_model = 'gemini-pro'
    else:
        target_model = available_models[0].replace('models/', '')

    model = genai.GenerativeModel(target_model)
    ai_aktif = True
except Exception as e:
    st.sidebar.error(f"Kritik Bağlantı Hatası: {str(e)}")
    ai_aktif = False

# ==========================================
# 4. VIP GİRİŞ EKRANI
# ==========================================
def check_access():
    user_ip = get_remote_ip()
    st.title("🔒 VIP Erişim Merkezi")
    st.write(f"Sistem IP Adresiniz: `{user_ip}`")

    if IP_WHITELIST and user_ip not in IP_WHITELIST and user_ip != "Bilinmiyor":
        st.error("❌ Bu IP adresi whitelist'te bulunmuyor. Erişim engellendi.")
        st.stop()

    passkey = st.text_input("Geçiş Anahtarınızı Girin:", type="password")
    
    if st.button("Sisteme Giriş Yap"):
        if passkey in VALID_PASSKEYS:
            st.session_state.auth = True
            st.success("Erişim onaylandı! Yükleniyor...")
            st.rerun()
        else:
            st.error("❌ Geçersiz anahtar!")

if not st.session_state.auth:
    check_access()
    st.stop()
    
# ==========================================
# 5. DİNAMİK AI FONKSİYONLARI (DİL DESTEKLİ)
# ==========================================

def ai_cumle_uret(seviye, hedef_dil):
    """Seçilen dile göre cümle üretir"""
    prompt = f"Bana {seviye} seviyesinde orta uzunlukta bir {hedef_dil} cümlesi ve Türkçesini ver. Format sadece şu olsun: 'yabancı_dil|türkçe'. Örn: 'I go|Gidiyorum' veya 'Ich gehe|Gidiyorum'."
    try:
        res = model.generate_content(prompt)
        raw = res.text.strip().replace('"', '').replace("*", "")
        if "|" in raw:
            target, tr = raw.split("|")
            return {"target": target.strip(), "tr": tr.strip()}
    except:
        return {"target": "Error", "tr": "Hata"}

def ai_cevap_kontrol_esnek(tahmin, dogru, tr, hedef_dil):
    """Seçilen dilin gramerine göre kontrol eder"""
    if not ai_aktif: return None
    prompt = f"""
    Sen harika bir {hedef_dil} öğretmenisin.
    Türkçe cümle: '{tr}'
    Beklenen {hedef_dil} karşılık: '{dogru}'
    Öğrencinin cevabı: '{tahmin}'
    
    TALİMAT:
    Eğer öğrencinin cevabı gramer ve anlam olarak doğruysa (kelime sırası biraz farklı olsa bile) sadece 'OK' yaz.
    Eğer yanlışsa, hatayı Türkçe olarak kısaca açıkla.
    """
    try:
        res = model.generate_content(prompt)
        return res.text.strip()
    except: return "AI şu an kontrol edemiyor."

def ai_kelime_bilmecesi_uret(seviye, hedef_dil):
    """Seçilen dilde kelime bilmecesi üretir"""
    prompt = f"Bana {seviye} seviyesinde bir {hedef_dil} kelimesi seç. Format: 'kelime|Türkçe karşılığı|İpucu({hedef_dil} dilinde)'. Örn: 'Apple|Elma|A red fruit'."
    try:
        res = model.generate_content(prompt)
        return res.text.strip().replace("*", "")
    except: return "Error|Hata|Try again"

# ==========================================
# 6. ARAYÜZ VE MODLAR
# ==========================================

st.sidebar.title("🤖 Master AI Dil Koçu")
st.sidebar.info(f"Model: {target_model}")

# --- DİL SEÇİMİ ---
hedef_dil = st.sidebar.radio("Öğrenmek istediğin dil:", ["İngilizce", "Almanca"])
flag = "🇬🇧" if hedef_dil == "İngilizce" else "🇩🇪"

st.sidebar.metric("🏆 Toplam Skor", st.session_state.skor)
mod = st.sidebar.radio("Oyun Modu Seç:", [f"Çeviri (TR -> {flag})", "Karışık Kelimeler", "Cümle Kurma", "AI Kelime Bilmecesi"])

if st.sidebar.button("Skoru Sıfırla"): st.session_state.skor = 0; st.rerun()

# --- MOD 1: ÇEVİRİ ---
if mod == f"Çeviri (TR -> {flag})":
    st.header(f"🌐 Türkçeden {hedef_dil}ye Çevir")
    seviye = st.selectbox("Seviye Seç:", ["A1", "A2", "B1", "B2", "C1"], key="ceviri_sev")
    
    if st.button("Yeni Cümle Üret ✨", key="ceviri_btn"):
        with st.spinner(f"AI {hedef_dil} cümlesi hazırlıyor..."):
            st.session_state.soru = ai_cumle_uret(seviye, hedef_dil)
            st.session_state.cevap_verildi = False
            st.rerun()
    
    if st.session_state.soru:
        s = st.session_state.soru
        st.subheader(f"🇹🇷 {s['tr']}")
        tahmin = st.text_input(f"{hedef_dil} karşılığını yazın:", key="ceviri_input")
        
        if st.button("Kontrol Et", key="ceviri_check"):
            with st.spinner("AI analiz ediyor..."):
                sonuc = ai_cevap_kontrol_esnek(tahmin, s['target'], s['tr'], hedef_dil)
                if "OK" in sonuc.upper():
                    st.success(f"✅ Harika! Doğru kabul edildi.\nÖrnek cevap: {s['target']}")
                    if not st.session_state.cevap_verildi:
                        st.session_state.skor += 20; st.session_state.cevap_verildi = True; st.balloons()
                else:
                    st.error(f"❌ Eksik veya hatalı!")
                    st.info(f"Öğretmen Notu: {sonuc}")

# --- MOD 2: KARIŞIK KELİMELER ---
elif mod == "Karışık Kelimeler":
    st.header(f"🔀 {hedef_dil} Kelimeleri Düzenle")
    seviye = st.selectbox("Seviye Seç:", ["A1", "A2", "B1", "B2", "C1"], key="mix_sev")
    
    if st.button("Yeni Soru Üret ✨", key="mix_btn"):
        with st.spinner("AI hazırlanıyor..."):
            st.session_state.soru = ai_cumle_uret(seviye, hedef_dil)
            st.session_state.cevap_verildi = False
            st.rerun()
        
    if st.session_state.soru:
        s = st.session_state.soru
        words = s['target'].split()
        random.shuffle(words)
        st.info(f"Kelimeler: {' / '.join(words)}")
        st.write(f"🇹🇷 Anlamı: {s['tr']}")
        
        tahmin = st.text_input("Doğru sıralamayı yazın:", key="mix_input")
        if st.button("Kontrol Et", key="mix_check"):
            if tahmin.lower().strip() == s['target'].lower().strip():
                st.success("✅ Tam isabet!")
                if not st.session_state.cevap_verildi: st.session_state.skor += 10; st.session_state.cevap_verildi = True
            else:
                st.error(f"Yanlış! Doğrusu: {s['target']}")

# --- MOD 3: CÜMLE KURMA (YAZMA) ---
elif mod == "Cümle Kurma":
    st.header("📝 Bak ve Yaz")
    seviye = st.selectbox("Seviye Seç:", ["A1", "A2", "B1", "B2", "C1"], key="look_sev")
    if st.button("Yeni Soru Üret ✨", key="look_btn"):
        with st.spinner("AI hazırlanıyor..."):
            st.session_state.soru = ai_cumle_uret(seviye, hedef_dil)
            st.session_state.cevap_verildi = False
            st.rerun()
    if st.session_state.soru:
        s = st.session_state.soru
        st.subheader(f"🇹🇷 {s['tr']}")
        st.write(f"{flag} {s['target']}")
        tahmin = st.text_input("Aynısını yazın:", key="look_input")
        if st.button("Kontrol Et", key="look_check"):
            if tahmin.strip() == s['target']: st.success("✅ Başarılı!"); st.session_state.skor += 5
            else: st.error("Harf hatası yaptın!")

# --- MOD 4: AI KELİME BİLMECESİ ---
elif mod == "AI Kelime Bilmecesi":
    st.header(f"🧠 AI {hedef_dil} Kelime Bilmecesi")
    seviye = st.selectbox("Seviye:", ["A1", "A2", "B1", "B2", "C1"], key="riddle_sev")
    
    if st.button("AI'dan Kelime İste ✨", key="riddle_btn"):
        with st.spinner("AI kelime seçiyor..."):
            raw = ai_kelime_bilmecesi_uret(seviye, hedef_dil)
            if "|" in raw:
                parts = raw.split("|")
                if len(parts) >= 3:
                    eng, tr, hint = parts[0], parts[1], parts[2]
                    st.session_state.kelime_bilmece = {"target": eng.strip(), "tr": tr.strip(), "hint": hint.strip()}
                    st.session_state.cevap_verildi = False
                    st.rerun()

    if st.session_state.kelime_bilmece:
        kb = st.session_state.kelime_bilmece
        st.info(f"💡 İpucu: {kb['hint']}")
        tahmin = st.text_input(f"Cevabınız ({hedef_dil} veya Türkçe):", key="riddle_input")
        
        if st.button("Tahmin Et", key="riddle_check"):
            t = tahmin.lower().strip()
            if t in kb['target'].lower() or t in kb['tr'].lower():
                st.success(f"🎉 BİLDİN! {kb['target']} = {kb['tr']}")
                if not st.session_state.cevap_verildi: st.session_state.skor += 25; st.session_state.cevap_verildi = True
            else:
                st.error("❌ Bilemedin, tekrar dene!")
