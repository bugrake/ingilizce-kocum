import streamlit as st
import random
import string
import difflib
import time

# ==========================================
# 1. SAYFA VE HAFIZA AYARLARI
# ==========================================
st.set_page_config(page_title="İngilizce Koçu", layout="centered")

# Streamlit hafızasını (Session State) başlatıyoruz
if 'skor' not in st.session_state: st.session_state.skor = 0
if 'soru' not in st.session_state: st.session_state.soru = None
if 'kelime_sorusu' not in st.session_state: st.session_state.kelime_sorusu = None
if 'cevap_verildi' not in st.session_state: st.session_state.cevap_verildi = False

# ==========================================
# 2. VERİTABANI (SANA AİT VERİLER)
# ==========================================

# CÜMLELER (SENTENCES) - Attığın tam liste
SENTENCES = {
    "A1": [
        {"eng": "My name is Sarah and I am twenty years old", "tr": "Adım Sarah ve yirmi yaşındayım"},
        {"eng": "There is a big table in the kitchen", "tr": "Mutfakta büyük bir masa var"},
        {"eng": "Do you like listening to pop music", "tr": "Pop müzik dinlemeyi sever misin"},
        {"eng": "She usually wakes up at seven o'clock", "tr": "O genellikle saat yedide uyanır"},
        {"eng": "My father does not work on Sundays", "tr": "Babam pazar günleri çalışmaz"},
        {"eng": "Can you help me with this heavy bag", "tr": "Bu ağır çanta için bana yardım edebilir misin"},
        {"eng": "They are playing football in the garden now", "tr": "Onlar şu an bahçede futbol oynuyorlar"},
        {"eng": "Where is the nearest bus station", "tr": "En yakın otobüs durağı nerede"},
        {"eng": "I have two brothers and one sister", "tr": "İki erkek ve bir kız kardeşim var"},
        {"eng": "This car is very expensive but beautiful", "tr": "Bu araba çok pahalı ama güzel"},
        {"eng": "Are you hungry or thirsty", "tr": "Aç mısın yoksa susadın mı"},
        {"eng": "The cat is sleeping under the chair", "tr": "Kedi sandalyenin altında uyuyor"},
        {"eng": "We go to the cinema every weekend", "tr": "Biz her hafta sonu sinemaya gideriz"},
        {"eng": "Please do not open the window", "tr": "Lütfen pencereyi açma"},
        {"eng": "What time does the movie start", "tr": "Film saat kaçta başlıyor"},
        {"eng": "I drink milk every morning", "tr": "Her sabah süt içerim"},
        {"eng": "My father is a doctor", "tr": "Babam bir doktordur"},
        {"eng": "Where is the nearest supermarket", "tr": "En yakın süpermarket nerede"},
        {"eng": "She has two brothers", "tr": "Onun iki erkek kardeşi var"},
        {"eng": "This blue pen is very cheap", "tr": "Bu mavi kalem çok ucuz"},
        {"eng": "I wake up at seven", "tr": "Saat yedide uyanırım"},
        {"eng": "The cat is on the sofa", "tr": "Kedi kanepenin üzerinde"},
        {"eng": "We go to school by bus", "tr": "Okula otobüsle gideriz"},
        {"eng": "I am very tired today", "tr": "Bugün çok yorgunum"},
        {"eng": "It is a beautiful day", "tr": "Güzel bir gün"},
        {"eng": "My mother cooks great pasta", "tr": "Annem harika makarna pişirir"},
        {"eng": "I love listening to music", "tr": "Müzik dinlemeyi severim"},
        {"eng": "Do you speak English", "tr": "İngilizce konuşuyor musun"},
        {"eng": "The book is under the table", "tr": "Kitap masanın altında"},
        {"eng": "He plays football every Sunday", "tr": "O her Pazar futbol oynar"},
        {"eng": "I have a big red car", "tr": "Büyük kırmızı bir arabam var"},
        {"eng": "Please open the window", "tr": "Lütfen pencereyi aç"},
        {"eng": "She wears a green dress", "tr": "O yeşil bir elbise giyiyor"},
        {"eng": "We are very happy now", "tr": "Şu an çok mutluyuz"},
        {"eng": "What time is it", "tr": "Saat kaç"},
        {"eng": "My favorite color is blue", "tr": "En sevdiğim renk mavidir"},
        {"eng": "I want to eat an apple", "tr": "Bir elma yemek istiyorum"},
        {"eng": "They live in a small house", "tr": "Küçük bir evde yaşıyorlar"},
        {"eng": "Can you help me please", "tr": "Bana yardım edebilir misin lütfen"},
        {"eng": "The weather is very hot", "tr": "Hava çok sıcak"},
        {"eng": "I see a bird in the tree", "tr": "Ağaçta bir kuş görüyorum"},
        {"eng": "Wait for me at the door", "tr": "Beni kapıda bekle"},
        {"eng": "He is my best friend", "tr": "O benim en iyi arkadaşım"},
        {"eng": "I don't like coffee", "tr": "Kahve sevmem"},
        {"eng": "This is a new smartphone", "tr": "Bu yeni bir akıllı telefon"},
        {"eng": "Look at the moon", "tr": "Aya bak"},
        {"eng": "I study English every day", "tr": "Her gün İngilizce çalışırım"},
        {"eng": "She is a beautiful girl", "tr": "O güzel bir kız"},
        {"eng": "We watch TV in the evening", "tr": "Akşamları TV izleriz"},
        {"eng": "There is a park near here", "tr": "Buranın yakınında bir park var"},
        {"eng": "My shoes are black", "tr": "Ayakkabılarım siyah"},
        {"eng": "I am hungry and thirsty", "tr": "Açım ve susadım"},
        {"eng": "Close your book please", "tr": "Kitabını kapat lütfen"},
        {"eng": "The dog is drinking water", "tr": "Köpek su içiyor"},
        {"eng": "I have ten fingers", "tr": "On parmağım var"},
        {"eng": "He works in an office", "tr": "O bir ofiste çalışıyor"},
        {"eng": "I need some money", "tr": "Biraz paraya ihtiyacım var"},
        {"eng": "Sit down on the chair", "tr": "Sandalyeye otur"},
        {"eng": "The sky is blue today", "tr": "Bugün gökyüzü mavi"},
        {"eng": "I go to bed at ten", "tr": "Saat onda yatarım"},
        {"eng": "Where is my bag", "tr": "Çantam nerede"},
        {"eng": "You are a good student", "tr": "Sen iyi bir öğrencisin"},
        {"eng": "I like reading books", "tr": "Kitap okumayı severim"},
        {"eng": "She has a pink umbrella", "tr": "Onun pembe bir şemsiyesi var"},
        {"eng": "Today is Monday", "tr": "Bugün Pazartesi"}
    ],
    "A2": [
        {"eng": "I visited my grandparents last summer", "tr": "Geçen yaz büyükanne ve büyükbabamı ziyaret ettim"},
        {"eng": "She was cooking dinner when I arrived", "tr": "Ben geldiğimde o akşam yemeği pişiriyordu"},
        {"eng": "Did you see the news on TV yesterday", "tr": "Dün televizyondaki haberleri gördün mü"},
        {"eng": "I think it will rain tomorrow afternoon", "tr": "Sanırım yarın öğleden sonra yağmur yağacak"},
        {"eng": "London is bigger than Manchester", "tr": "Londra Manchester'dan daha büyüktür"},
        {"eng": "You must wear a uniform at school", "tr": "Okulda üniforma giymelisin"},
        {"eng": "I have never eaten sushi before", "tr": "Daha önce hiç suşi yemedim"},
        {"eng": "Is she going to buy a new laptop", "tr": "O yeni bir dizüstü bilgisayar alacak mı"},
        {"eng": "He runs faster than anyone else in the class", "tr": "O sınıftaki herkesten daha hızlı koşar"},
        {"eng": "We were not watching a movie last night", "tr": "Dün gece film izlemiyorduk"},
        {"eng": "Have you ever been to Italy", "tr": "Hiç İtalya'da bulundun mu"},
        {"eng": "I would like to order a cup of coffee", "tr": "Bir fincan kahve sipariş etmek istiyorum"},
        {"eng": "This represents the best day of my life", "tr": "Bu hayatımın en güzel gününü temsil ediyor"},
        {"eng": "You should see a dentist for your toothache", "tr": "Diş ağrın için bir dişçiye görünmelisin"},
        {"eng": "Why were you crying in the room", "tr": "Oda neden ağlıyordun"},
        {"eng": "I visited my grandparents last weekend.", "tr": "Geçen hafta sonu büyükanne ve büyükbabamı ziyaret ettim."},
        {"eng": "You should wear a coat because it's raining.", "tr": "Ceket giymelisin çünkü yağmur yağıyor."},
        {"eng": "I have been to London twice.", "tr": "İki kez Londra'da bulundum."},
        {"eng": "She was cooking when the phone rang.", "tr": "Telefon çaldığında yemek pişiriyordu."},
        {"eng": "I think this movie is more boring than the last one.", "tr": "Bence bu film sonuncusundan daha sıkıcı."},
        {"eng": "He is going to start a new job next month.", "tr": "Gelecek ay yeni bir işe başlayacak."},
        {"eng": "We decided to stay at home and rest.", "tr": "Evde kalıp dinlenmeye karar verdik."},
        {"eng": "Did you finish your homework yesterday?", "tr": "Ödevini dün bitirdin mi?"},
        {"eng": "I need to buy some ingredients for the dinner.", "tr": "Akşam yemeği için bazı malzemeler almam gerekiyor."},
        {"eng": "There are fewer people in the museum today.", "tr": "Bugün müzede daha az insan var."},
        {"eng": "Can you tell me the way to the station?", "tr": "Bana istasyona giden yolu söyleyebilir misin?"},
        {"eng": "I forgot to call him this morning.", "tr": "Bu sabah onu aramayı unuttum."},
        {"eng": "They were walking in the park at 5 PM.", "tr": "Saat 5'te parkta yürüyorlardı."},
        {"eng": "This car is the most expensive in the gallery.", "tr": "Bu araba galerideki en pahalı olanı."},
        {"eng": "I would like to travel around the world.", "tr": "Dünyayı gezmek isterim."},
        {"eng": "She speaks English better than me.", "tr": "İngilizceyi benden daha iyi konuşuyor."},
        {"eng": "Wait a minute, I am checking my emails.", "tr": "Bir dakika bekle, e-postalarımı kontrol ediyorum."},
        {"eng": "We spent all our money during the holiday.", "tr": "Tatil boyunca tüm paramızı harcadık."},
        {"eng": "If it doesn't rain, we will go for a walk.", "tr": "Eğer yağmur yağmazsa yürüyüşe çıkacağız."},
        {"eng": "I lost my wallet while I was shopping.", "tr": "Alışveriş yaparken cüzdanımı kaybettim."},
        {"eng": "He is taller than his older brother.", "tr": "O, ağabeyinden daha uzun."},
        {"eng": "Do you know how to use this machine?", "tr": "Bu makinenin nasıl kullanılacağını biliyor musun?"},
        {"eng": "I have never eaten Mexican food before.", "tr": "Daha önce hiç Meksika yemeği yemedim."},
        {"eng": "She is looking for a new apartment.", "tr": "Yeni bir daire arıyor."},
        {"eng": "The hotel was very comfortable and clean.", "tr": "Otel çok konforlu ve temizdi."},
        {"eng": "We must arrive at the airport on time.", "tr": "Havalimanına zamanında varmalıyız."},
        {"eng": "Everything was very different ten years ago.", "tr": "On yıl önce her şey çok farklıydı."},
        {"eng": "I hope you enjoy your stay here.", "tr": "Umarım buradaki konaklamanızdan keyif alırsınız."},
        {"eng": "What did you do during the summer break?", "tr": "Yaz tatili boyunca ne yaptın?"},
        {"eng": "I am not interested in history.", "tr": "Tarih ile ilgilenmiyorum."},
        {"eng": "I visited my uncle last week", "tr": "Geçen hafta amcamı ziyaret ettim"},
        {"eng": "You should wear a coat", "tr": "Ceket giymelisin"},
        {"eng": "I have been to Paris once", "tr": "Bir kez Paris'te bulundum"},
        {"eng": "She was sleeping when I arrived", "tr": "Ben vardığımda o uyuyordu"},
        {"eng": "This movie is better than the other", "tr": "Bu film diğerinden daha iyi"},
        {"eng": "I am going to buy a new bike", "tr": "Yeni bir bisiklet satın alacağım"},
        {"eng": "We decided to stay at a hotel", "tr": "Bir otelde kalmaya karar verdik"},
        {"eng": "Did you finish your project", "tr": "Projemi bitirdin mi"},
        {"eng": "I need to buy some eggs", "tr": "Biraz yumurta almam gerekiyor"},
        {"eng": "There are fewer students today", "tr": "Bugün daha az öğrenci var"},
        {"eng": "Can you show me the way", "tr": "Bana yolu gösterebilir misin"},
        {"eng": "I forgot my phone at home", "tr": "Telefonumu evde unuttum"},
        {"eng": "They were playing in the garden", "tr": "Bahçede oynuyorlardı"},
        {"eng": "This is the most expensive car", "tr": "Bu en pahalı araba"},
        {"eng": "I would like to drink orange juice", "tr": "Portakal suyu içmek isterim"},
        {"eng": "She speaks faster than me", "tr": "Benden daha hızlı konuşuyor"},
        {"eng": "Wait a minute I am coming", "tr": "Bir dakika bekle geliyorum"},
        {"eng": "We spent a lot of money", "tr": "Çok para harcadık"},
        {"eng": "If it rains we will stay home", "tr": "Eğer yağmur yağarsa evde kalacağız"},
        {"eng": "I lost my key yesterday", "tr": "Dün anahtarımı kaybettim"},
        {"eng": "He is taller than his father", "tr": "O babasından daha uzun"},
        {"eng": "Do you know how to swim", "tr": "Yüzmeyi biliyor musun"},
        {"eng": "I have never seen a lion", "tr": "Daha önce hiç aslan görmedim"},
        {"eng": "She is looking for her glasses", "tr": "Gözlüklerini arıyor"},
        {"eng": "The hotel was very clean", "tr": "Otel çok temizdi"},
        {"eng": "We must leave the house now", "tr": "Evden şimdi ayrılmalıyız"},
        {"eng": "Everything was cheaper before", "tr": "Eskiden her şey daha ucuzdu"},
        {"eng": "I hope you like the gift", "tr": "Umarım hediyeyi beğenirsin"},
        {"eng": "What did you do last night", "tr": "Dün gece ne yaptın"},
        {"eng": "I am not interested in sports", "tr": "Sporla ilgilenmiyorum"},
        {"eng": "He was watching a movie alone", "tr": "Yalnız başına film izliyordu"},
        {"eng": "She has to go to the dentist", "tr": "Dişçiye gitmek zorunda"},
        {"eng": "I will call you later", "tr": "Seni sonra arayacağım"},
        {"eng": "They are planning a trip", "tr": "Bir gezi planlıyorlar"},
        {"eng": "This box is too heavy", "tr": "Bu kutu çok ağır"},
        {"eng": "I usually have lunch at noon", "tr": "Genelde öğlen yemeği yerim"},
        {"eng": "We enjoyed the party a lot", "tr": "Partiden çok keyif aldık"},
        {"eng": "You look very tired today", "tr": "Bugün çok yorgun görünüyorsun"},
        {"eng": "I am afraid of spiders", "tr": "Örümceklerden korkarım"},
        {"eng": "The train leaves at six", "tr": "Tren saat altıda kalkıyor"},
        {"eng": "She is older than her sister", "tr": "O kız kardeşinden daha büyük"},
        {"eng": "I bought a gift for you", "tr": "Senin için bir hediye aldım"},
        {"eng": "We had a great time together", "tr": "Birlikte harika vakit geçirdik"},
        {"eng": "Do you have any brothers", "tr": "Hiç erkek kardeşin var mı"},
        {"eng": "I am cleaning my room now", "tr": "Şimdi odamı temizliyorum"},
        {"eng": "He can play the piano well", "tr": "Piyanoyu iyi çalabiliyor"},
        {"eng": "She doesn't want to go out", "tr": "Dışarı çıkmak istemiyor"},
        {"eng": "It was raining all day", "tr": "Tüm gün yağmur yağıyordu"},
        {"eng": "I am waiting for the bus", "tr": "Otobüsü bekliyorum"},
        {"eng": "They are my new neighbors", "tr": "Onlar benim yeni komşularım"}
    ],
    "B1": [
        {"eng": "If I win the lottery I will buy a house", "tr": "Piyangoyu kazanırsam bir ev alacağım"},
        {"eng": "This bridge was built by the Romans", "tr": "Bu köprü Romalılar tarafından inşa edildi"},
        {"eng": "I have been working here for ten years", "tr": "On yıldır burada çalışıyorum"},
        {"eng": "She asked me where I was going", "tr": "Bana nereye gittiğimi sordu"},
        {"eng": "You do not have to bring food", "tr": "Yiyecek getirmek zorunda değilsin"},
        {"eng": "The man who called yesterday is my boss", "tr": "Dün arayan adam benim patronum"},
        {"eng": "I used to play the guitar when I was young", "tr": "Gençken gitar çalardım"},
        {"eng": "It might be too late to catch the train", "tr": "Treni yakalamak için çok geç olabilir"},
        {"eng": "She made me clean the whole house", "tr": "Bana bütün evi temizletti"},
        {"eng": "I am looking forward to seeing you again", "tr": "Seni tekrar görmeyi dört gözle bekliyorum"},
        {"eng": "Unless you hurry we will miss the bus", "tr": "Acele etmezsen otobüsü kaçıracağız"},
        {"eng": "He must have forgotten the meeting", "tr": "Toplantıyı unutmuş olmalı"},
        {"eng": "Do you mind if I open the window", "tr": "Pencereyi açmamın bir sakıncası var mı"},
        {"eng": "I prefer tea to coffee in the mornings", "tr": "Sabahları çayı kahveye tercih ederim"},
        {"eng": "The book was so boring that I fell asleep", "tr": "Kitap o kadar sıkıcıydı ki uyuyakaldım"},
        {"eng": "I am used to waking up early every day.", "tr": "Her gün erken uyanmaya alışkınım."},
        {"eng": "If I had enough money, I would buy a boat.", "tr": "Yeterli param olsaydı bir tekne alırdım."},
        {"eng": "The book which I borrowed from the library is great.", "tr": "Kütüphaneden ödünç aldığım kitap harika."},
        {"eng": "He apologized for being late to the meeting.", "tr": "Toplantıya geç kaldığı için özür diledi."},
        {"eng": "I don't think it is necessary to call them now.", "tr": "Şu an onları aramanın gerekli olduğunu düşünmüyorum."},
        {"eng": "The problem has been solved by the technical team.", "tr": "Problem teknik ekip tarafından çözüldü."},
        {"eng": "Although it was raining, we went out.", "tr": "Yağmur yağmasına rağmen dışarı çıktık."},
        {"eng": "I am looking forward to hearing from you soon.", "tr": "En kısa sürede sizden haber almayı bekliyorum."},
        {"eng": "He explained why he couldn't finish the report.", "tr": "Raporu neden bitiremediğini açıkladı."},
        {"eng": "She suggested going to a different restaurant.", "tr": "Farklı bir restorana gitmeyi önerdi."},
        {"eng": "I have been working here for five years.", "tr": "Beş yıldır burada çalışıyorum."},
        {"eng": "You are not allowed to smoke in this area.", "tr": "Bu alanda sigara içmenize izin verilmez."},
        {"eng": "I wonder if they will accept our offer.", "tr": "Teklifimizi kabul edip etmeyeceklerini merak ediyorum."},
        {"eng": "It was such a boring movie that I fell asleep.", "tr": "O kadar sıkıcı bir filmdi ki uyuyakaldım."},
        {"eng": "The more you practice, the better you get.", "tr": "Ne kadar çok pratik yaparsan o kadar iyi olursun."},
        {"eng": "I managed to fix the computer by myself.", "tr": "Bilgisayarı kendi başıma tamir etmeyi başardım."},
        {"eng": "Neither my brother nor my sister likes jazz.", "tr": "Ne erkek kardeşim ne de kız kardeşim caz sever."},
        {"eng": "The weather is expected to be sunny tomorrow.", "tr": "Yarının güneşli olması bekleniyor."},
        {"eng": "I am not sure whether he is coming or not.", "tr": "Gelip gelmeyeceğinden emin değilim."},
        {"eng": "You should avoid eating too much sugar.", "tr": "Çok fazla şeker yemekten kaçınmalısın."},
        {"eng": "He denied stealing the money from the desk.", "tr": "Masadan parayı çaldığını reddetti."},
        {"eng": "This is the most interesting book I have ever read.", "tr": "Bu şimdiye kadar okuduğum en ilginç kitap."},
        {"eng": "I was surprised to see him at the party.", "tr": "Onu partide gördüğüme şaşırdım."},
        {"eng": "We need to discuss the project details.", "tr": "Proje detaylarını tartışmamız gerekiyor."},
        {"eng": "By the time we arrived, the train had left.", "tr": "Biz vardığımızda tren kalkmıştı."},
        {"eng": "I prefer tea to coffee in the mornings.", "tr": "Sabahları çayı kahveye tercih ederim."},
        {"eng": "She is responsible for the marketing department.", "tr": "Pazarlama departmanından o sorumlu."},
        {"eng": "You don't have to bring anything with you.", "tr": "Yanında hiçbir şey getirmene gerek yok."},
        {"eng": "I have no intention of changing my mind.", "tr": "Fikrimi değiştirmeye niyetim yok."},
        {"eng": "The results will be announced next Monday.", "tr": "Sonuçlar önümüzdeki Pazartesi açıklanacak."},
        {"eng": "I am used to living alone", "tr": "Yalnız yaşamaya alışkınım"},
        {"eng": "If I were you I would go", "tr": "Senin yerinde olsam giderdim"},
        {"eng": "The man who lives here is old", "tr": "Burada yaşayan adam yaşlı"},
        {"eng": "He apologized for his mistake", "tr": "Hatası için özür diledi"},
        {"eng": "I don't think it is necessary", "tr": "Bunun gerekli olduğunu düşünmüyorum"},
        {"eng": "The window was broken by them", "tr": "Pencere onlar tarafından kırıldı"},
        {"eng": "Although it was late we worked", "tr": "Geç olmasına rağmen çalıştık"},
        {"eng": "I look forward to seeing you", "tr": "Seni görmeyi dört gözle bekliyorum"},
        {"eng": "He explained the reason to me", "tr": "Sebebi bana açıkladı"},
        {"eng": "She suggested going to the park", "tr": "Parka gitmeyi önerdi"},
        {"eng": "I have been working for hours", "tr": "Saatlerdir çalışıyorum"},
        {"eng": "You are not allowed to enter", "tr": "Girmene izin verilmiyor"},
        {"eng": "I wonder what they are doing", "tr": "Ne yaptıklarını merak ediyorum"},
        {"eng": "It was such a boring day", "tr": "O kadar sıkıcı bir gündü ki"},
        {"eng": "The more you read the more you learn", "tr": "Ne kadar okursan o kadar öğrenirsin"},
        {"eng": "I managed to solve the problem", "tr": "Sorunu çözmeyi başardım"},
        {"eng": "Neither tea nor coffee is good", "tr": "Ne çay ne de kahve iyidir"},
        {"eng": "It is expected to be snowy", "tr": "Karlı olması bekleniyor"},
        {"eng": "I am not sure about that", "tr": "Bu konuda emin değilim"},
        {"eng": "You should avoid smoking here", "tr": "Burada sigara içmekten kaçınmalısın"},
        {"eng": "He denied stealing the car", "tr": "Arabayı çaldığını reddetti"},
        {"eng": "This is the best book ever", "tr": "Bu şimdiye kadarki en iyi kitap"},
        {"eng": "I was surprised by the news", "tr": "Haberlere şaşırdım"},
        {"eng": "We need to discuss the price", "tr": "Fiyatı tartışmamız gerekiyor"},
        {"eng": "By the time he came I left", "tr": "O geldiğinde ben çıkmıştım"},
        {"eng": "I prefer tea to coffee", "tr": "Çayı kahveye tercih ederim"},
        {"eng": "She is responsible for the baby", "tr": "Bebekten o sorumlu"},
        {"eng": "You don't have to wait for me", "tr": "Beni beklemek zorunda değilsin"},
        {"eng": "I have no intention of leaving", "tr": "Ayrılmaya niyetim yok"},
        {"eng": "The winner will be announced soon", "tr": "Kazanan yakında açıklanacak"},
        {"eng": "I am interested in art history", "tr": "Sanat tarihiyle ilgileniyorum"},
        {"eng": "He warned me about the weather", "tr": "Beni hava durumu hakkında uyardı"},
        {"eng": "She decided to study medicine", "tr": "Tıp okumaya karar verdi"},
        {"eng": "I had my hair cut yesterday", "tr": "Dün saçımı kestirdim"},
        {"eng": "It is worth seeing this museum", "tr": "Bu müzeyi görmeye değer"},
        {"eng": "They seem to be very happy", "tr": "Çok mutlu görünüyorlar"},
        {"eng": "I can't afford a new car", "tr": "Yeni bir arabaya gücüm yetmez"},
        {"eng": "He is capable of doing this", "tr": "Bunu yapmaya yetenekli"},
        {"eng": "I am bored with this game", "tr": "Bu oyundan sıkıldım"},
        {"eng": "She insisted on paying the bill", "tr": "Hesabı ödemekte ısrar etti"},
        {"eng": "I used to play guitar", "tr": "Eskiden gitar çalardım"},
        {"eng": "The film was quite interesting", "tr": "Film oldukça ilginçti"},
        {"eng": "I will let you know tomorrow", "tr": "Yarın sana haber vereceğim"},
        {"eng": "He is good at solving puzzles", "tr": "Bulmaca çözmede iyidir"},
        {"eng": "I forgot to lock the door", "tr": "Kapıyı kilitlemeyi unuttum"},
        {"eng": "She wants to travel the world", "tr": "Dünyayı gezmek istiyor"},
        {"eng": "We need to find a solution", "tr": "Bir çözüm bulmamız gerekiyor"},
        {"eng": "I am proud of your success", "tr": "Başarınla gurur duyuyorum"},
        {"eng": "He is afraid of losing his job", "tr": "İşini kaybetmekten korkuyor"},
        {"eng": "It is difficult to learn a language", "tr": "Bir dil öğrenmek zordur"}
    ],
    "B2": [
        {"eng": "If I were you I would apologize to her immediately", "tr": "Senin yerinde olsam ondan hemen özür dilerdim"},
        {"eng": "By the time we arrived the film had already started", "tr": "Biz vardığımızda film çoktan başlamıştı"},
        {"eng": "I wish I had studied harder for the exam", "tr": "Keşke sınava daha sıkı çalışsaydım"},
        {"eng": "She is used to waking up early in the morning", "tr": "O sabahları erken uyanmaya alışıktır"},
        {"eng": "Despite the heavy rain they continued the match", "tr": "Şiddetli yağmura rağmen maça devam ettiler"},
        {"eng": "You had better see a doctor before it gets worse", "tr": "Kötüleşmeden önce bir doktora görünsen iyi olur"},
        {"eng": "It is said that he is a millionaire", "tr": "Onun bir milyoner olduğu söyleniyor (söylenti)"},
        {"eng": "Not only is he smart but he is also very funny", "tr": "O sadece zeki değil aynı zamanda çok da komiktir"},
        {"eng": "I regret not telling you the truth earlier", "tr": "Sana gerçeği daha önce söylemediğim için pişmanım"},
        {"eng": "Having finished his work he went home", "tr": "İşini bitirince eve gitti"},
        {"eng": "I would rather stay home than go out tonight", "tr": "Bu gece dışarı çıkmaktansa evde kalmayı tercih ederim"},
        {"eng": "Hardly had I entered the room when the phone rang", "tr": "Odaya daha yeni girmiştim ki telefon çaldı"},
        {"eng": "Suppose you lost your job what would you do", "tr": "Diyelim ki işini kaybettin ne yapardın"},
        {"eng": "It is high time we went home", "tr": "Eve gitme vaktimiz çoktan geldi"},
        {"eng": "He acts as if he knows everything", "tr": "Her şeyi biliyormuş gibi davranıyor"},
        {"eng": "Despite the challenges, the project was a success.", "tr": "Zorluklara rağmen proje bir başarıydı."},
        {"eng": "I would rather you didn't tell anyone about this.", "tr": "Bunu kimseye anlatmamanı tercih ederim."},
        {"eng": "It is about time we took some action regarding this.", "tr": "Bu konuda harekete geçmemizin vakti geldi."},
        {"eng": "Hardly had I entered the room when the phone rang.", "tr": "Odaya girer girmez telefon çaldı."},
        {"eng": "The government is considering implementing new laws.", "tr": "Hükümet yeni yasaları uygulamayı düşünüyor."},
        {"eng": "She is said to be the most talented artist in town.", "tr": "Kasabadaki en yetenekli sanatçı olduğu söyleniyor."},
        {"eng": "I regret not taking the opportunity when I had it.", "tr": "Fırsatım varken onu değerlendirmediğim için pişmanım."},
        {"eng": "Providing that you work hard, you will succeed.", "tr": "Çok çalışman şartıyla başarılı olacaksın."},
        {"eng": "The evidence suggests that he was not involved.", "tr": "Kanıtlar onun dahil olmadığını gösteriyor."},
        {"eng": "I must have left my phone at the office.", "tr": "Telefonumu ofiste bırakmış olmalıyım."},
        {"eng": "In spite of the heavy traffic, we arrived on time.", "tr": "Yoğun trafiğe rağmen zamanında vardık."},
        {"eng": "They are likely to postpone the match due to rain.", "tr": "Yağmur nedeniyle maçı ertelemeleri muhtemel."},
        {"eng": "The company has undergone significant changes lately.", "tr": "Şirket son zamanlarda önemli değişiklikler geçirdi."},
        {"eng": "I object to being treated like a child.", "tr": "Çocuk gibi muamele görmeye itiraz ediyorum."},
        {"eng": "Had I known the truth, I wouldn't have acted like that.", "tr": "Gerçeği bilseydim öyle davranmazdım."}
    ]
}

# GRAMER İPUÇLARI (GRAMMAR TIPS)
GRAMMAR_TIPS = {
    # Zaman İpuçları
    "every morning": "💡 DERS NOTU: 'Every morning' bir rutindir. Geniş Zaman (Simple Present) kullanmalısın. I/You/We/They için fiil yalın kalır.",
    "every day": "💡 DERS NOTU: 'Every day' (Her gün) sıklık bildirir. Özne He/She/It ise fiile mutlaka -s, -es veya -ies eklemelisin.",
    "now": "💡 DERS NOTU: 'Now' (Şu an) Şimdiki Zaman (Present Continuous) işaretidir. Formül: am/is/are + Fiil-ING.",
    "usually": "💡 DERS NOTU: 'Usually' (Genellikle) bir sıklık zarfıdır. Özne ile fiil arasına yazılır: 'She usually wakes up...'",
    
    # Edatlar (Prepositions) - Yer ve Zaman
    "on sundays": "💡 DERS NOTU: Günlerden önce daima 'on' kullanılır. (On Mondays, on Sundays vb.)",
    "at seven": "💡 DERS NOTU: Saatlerden önce daima 'at' edatı kullanılır. (At 9 o'clock, at 7:30 vb.)",
    "in the kitchen": "💡 DERS NOTU: Odalar ve kapalı alanlar için 'in' kullanılır. (In the garden, in the room vb.)",
    "under the": "💡 DERS NOTU: 'Under' (Altında) demektir. 'The cat is under the chair' (Kedi sandalyenin altında).",
    "near our": "💡 DERS NOTU: 'Near' (Yakınında) demektir. 'Near'dan sonra 'to' gelmez, direkt yer ismi gelir.",
    "at the bus stop": "💡 DERS NOTU: Otobüs durağı gibi 'nokta' atışı yerlerde 'at' kullanılır.",
    
    # Yapısal Kurallar (A1 Seviye)
    "there is": "💡 DERS NOTU: Tekil nesneler için 'There is' (Var), çoğul nesneler için 'There are' kullanılır.",
    "does not": "💡 DERS NOTU: Geniş zamanda olumsuz yaparken 'He/She/It' için 'does not' (doesn't) gelir ve fiildeki -s takısı düşer!",
    "do you": "💡 DERS NOTU: Geniş zamanda soru sorarken I/You/We/They için 'Do' ile başla.",
    "what time": "💡 DERS NOTU: 'What time' (Saat kaçta) sorusudur. Eylem bildiren cümlelerde 'What time does...' yapısını kontrol et.",
    "can you": "💡 DERS NOTU: 'Can' yetenek veya rica bildirir. 'Can'den sonra gelen fiil hiçbir ek almaz (yalın hal).",
    "listening to": "💡 DERS NOTU: 'Listen' (Dinlemek) fiili her zaman 'to' edatı ile kullanılır: 'Listen to music'.",
    "too hot to": "💡 DERS NOTU: 'Too + Sıfat + to + Fiil' kalıbı, bir şeyin bir eylemi yapmak için 'fazlasıyla/aşırı' olduğunu anlatır.",
    
    # İyelik ve Kişiler
    "father's name": "💡 DERS NOTU: İsimlere gelen ('s) takısı iyelik (aitlik) bildirir. 'Babanın adı' gibi.",
    "my sister": "💡 DERS NOTU: 'My' (Benim), 'Your' (Senin), 'His' (Onun-Erkek), 'Her' (Onun-Kadın) iyelik zamirleridir.",
    "named": "💡 DERS NOTU: 'Named Max' (Max adında/isimli) anlamına gelir. Bir şeyin adını söylerken kullanılır.",

    # --- YER VE YÖN EDATLARI (Prepositions) ---
    "in the garden": "💡 DERS NOTU: 'Garden' (Bahçe) sınırları belli bir alan olduğu için 'in' kullanılır.",
    "on the sofa": "💡 DERS NOTU: Bir yüzeyin 'üzerinde' olma durumunda 'on' kullanılır (On the chair, on the table).",
    "at the airport": "💡 DERS NOTU: Havaalanı, durak veya belirli bir bina gibi 'varış/bulunma noktaları' için 'at' tercih edilir.",
    "by bus": "💡 DERS NOTU: Ulaşım araçlarıyla bir yere gitmekten bahsederken 'by' kullanılır (By train, by car, by plane).",
    "wait for": "💡 DERS NOTU: 'Wait' (Beklemek) fiili nesne alırken mutlaka 'for' ile kullanılır: 'Wait for me'.",

    # --- ZAMAN VE SÜREÇ (Time Expressions) ---
    "during": "💡 DERS NOTU: 'During' (Boyunca/Esnasında) bir zaman dilimini anlatır. Kendisinden sonra cümle değil, isim gelir.",
    "by the time": "💡 DERS NOTU: '-e kadar' veya 'olduğunda' anlamındadır. Past Perfect (had V3) ile kullanımı çok yaygındır.",
    "until": "💡 DERS NOTU: Bir eylemin ne zamana kadar devam ettiğini belirtir.",
    "at noon": "💡 DERS NOTU: Günün belli vakitlerinde 'at' kullanılır: at noon (öğlen), at night (gece).",

    # --- SIFAT VE ZARF TUZAKLARI ---
    "expensive but": "💡 DERS NOTU: 'But' (Ama) zıtlık bildirir. Bir olumlu bir olumsuz durumu birbirine bağlar.",
    "too heavy": "💡 DERS NOTU: 'Too' sıfattan önce gelirse 'aşırı/olumsuz derecede çok' anlamı katar.",
    "enough": "💡 DERS NOTU: 'Enough' (Yeterli) sıfattan sonra gelir: 'Good enough' (Yeterince iyi).",
    "interested in": "💡 DERS NOTU: 'İlgili olmak' derken daima 'in' edatı kullanılır: 'I am interested in art'.",
    "good at": "💡 DERS NOTU: Bir şeyde iyi olduğunuzu söylerken 'in' değil 'at' kullanılır: 'Good at math'.",

    # --- MODALS & STRUCTURES (B1-B2) ---
    "used to live": "💡 DERS NOTU: Eskiden olan ama artık olmayan durumları anlatır. 'I used to live' (Eskiden yaşardım).",
    "am used to": "💡 DERS NOTU: 'Be used to + ING' bir şeye 'alışkın olmayı' ifade eder. 'I am used to living' (Yaşamaya alışkınım).",
    "have to": "💡 DERS NOTU: Dışarıdan gelen bir zorunluluğu (yasa, kural vb.) anlatırken kullanılır.",
    "must have left": "💡 DERS NOTU: Geçmişe dair 'güçlü bir tahmin' bildirir: 'Bırakmış olmalıyım'.",
    "regret not": "💡 DERS NOTU: 'Regret + not + V-ing' yapısı geçmişte yapmadığın bir şeyden pişmanlık duyduğunu anlatır.",
    "suppose you": "💡 DERS NOTU: 'Diyelim ki/Varsayalım ki' anlamında bir varsayım (Hypothesis) cümlesi başlatır.",
    "it is worth": "💡 DERS NOTU: '... yapmaya değer' kalıbıdır. Kendisinden sonra gelen fiil mutlaka -ING alır.",
    "object to": "💡 DERS NOTU: Bir şeye itiraz etmek. Buradaki 'to' edat olduğu için arkasından fiil gelirse -ING alır.",
    
    # --- A1 SEVİYESİ İPUÇLARI ---
    "every": "💡 DERS NOTU: 'Every' (Her) geniş zaman ipucusudur. Rutinleri anlatır.",
    "there is": "💡 DERS NOTU: Tekil nesneler için 'There is', çoğul nesneler için 'There are' kullanılır.",
    "usually": "💡 DERS NOTU: Sıklık zarfları (usually, always vb.) genellikle özne ile fiil arasına gelir.",
    "does not": "💡 DERS NOTU: He/She/It için olumsuzlarda 'does not' gelir ve fiil yalın kalır (S takısı düşer).",
    "can you": "💡 DERS NOTU: 'Can' yetenek veya rica bildirir. Fiil daima yalın haldedir.",
    "now": "💡 DERS NOTU: 'Now' (Şu an) şimdiki zamanı bildirir. am/is/are + fiil-ING yapısını unutma.",
    "near": "💡 DERS NOTU: 'Near' (Yakınında) edatından sonra 'to' gelmez, direkt yer ismi gelir.",
    "under": "💡 DERS NOTU: 'Under' bir şeyin altında olmayı ifade eder.",
    "on sundays": "💡 DERS NOTU: Günlerden önce daima 'ON' kullanılır.",
    "at seven": "💡 DERS NOTU: Saatlerden önce daima 'AT' kullanılır.",
    "too hot": "💡 DERS NOTU: 'Too' sıfatın önüne gelerek 'aşırı/gereğinden fazla' anlamı katar.",

    # --- A2 SEVİYESİ İPUÇLARI ---
    "last": "💡 DERS NOTU: 'Last' (Geçen) geçmiş zaman (Simple Past) işaretidir. Fiilin 2. halini kullanmalısın.",
    "was cooking": "💡 DERS NOTU: Past Continuous (Was/Were + ING) geçmişte devam eden olayları anlatır.",
    "than": "💡 DERS NOTU: 'Than' karşılaştırma (Comparative) yaparken kullanılır. (Better than, faster than vb.)",
    "must": "💡 DERS NOTU: 'Must' zorunluluk bildirir. Güçlü bir gereklilik söz konusudur.",
    "never": "💡 DERS NOTU: 'Have never' daha önce hiç yapılmamış deneyimleri anlatır (Present Perfect).",
    "going to": "💡 DERS NOTU: Planlı gelecek zamanı (am/is/are going to) anlatırken kullanılır.",
    "should": "💡 DERS NOTU: Tavsiye verirken 'should' kullanılır. 'Ceket giymelisin' gibi.",
    "most": "💡 DERS NOTU: En üstünlük (Superlative) bildirir. Genelde 'the' ile kullanılır (The most expensive).",
    "ago": "💡 DERS NOTU: 'Ago' (Önce) kelimesi cümlenin sonunda yer alır ve geçmiş zamanı belirtir.",
    "while": "💡 DERS NOTU: 'While' (İken) genellikle Past Continuous (was/were ing) ile kullanılır.",

    # --- B1 SEVİYESİ İPUÇLARI ---
    "if i": "💡 DERS NOTU: Conditional (Koşul) cümleleridir. If + Present, Will / If + Past, Would.",
    "built by": "💡 DERS NOTU: Edilgen yapı (Passive Voice). Nesne + be + V3 + by + fail.",
    "for ten years": "💡 DERS NOTU: 'For' süreci anlatır. Present Perfect Continuous ile kullanımı yaygındır.",
    "who": "💡 DERS NOTU: Relative Clause (Sıfat Cümleciği). 'Who' insanları nitelemek için kullanılır.",
    "used to": "💡 DERS NOTU: Eskiden yapılan ama artık bırakılan alışkanlıkları anlatır.",
    "might": "💡 DERS NOTU: Düşük ihtimal bildiren bir modal yapısıdır.",
    "looking forward to": "💡 DERS NOTU: 'Dört gözle beklemek'. Dikkat: 'to' dan sonra fiil -ING alır!",
    "unless": "💡 DERS NOTU: '-medikçe / -mazsa' anlamına gelir. 'If not'ın yerine kullanılır.",
    "prefer": "💡 DERS NOTU: Prefer (neyi) to (neye). 'Prefer tea to coffee' (Çayı kahveye tercih ederim).",
    "so boring that": "💡 DERS NOTU: 'O kadar ... ki' yapısıdır. So + Sıfat + That + Cümle.",
    "neither": "💡 DERS NOTU: 'Neither... nor...' (Ne o... ne diğeri...). Olumsuz bir seçim sunar.",

    # --- B2 SEVİYESİ İPUÇLARI ---
    "wish i had": "💡 DERS NOTU: Geçmişteki bir pişmanlığı (Wish + Past Perfect) ifade eder.",
    "despite": "💡 DERS NOTU: '-e rağmen' anlamına gelir. Kendisinden sonra isim veya isim tamlaması gelir.",
    "had better": "💡 DERS NOTU: 'Yapsan iyi olur' anlamında güçlü bir uyarıdır. Fiil yalındır.",
    "it is said": "💡 DERS NOTU: Genel kanı veya söylentileri anlatmak için kullanılan edilgen yapıdır.",
    "not only": "💡 DERS NOTU: 'Not only... but also...' (Sadece ... değil, aynı zamanda ...).",
    "regret": "💡 DERS NOTU: 'Regret' fiilinden sonra -ING gelirse geçmişteki bir eylemden duyulan pişmanlığı anlatır.",
    "rather than": "💡 DERS NOTU: 'Tercihen' anlamındadır. Bir seçeneği diğerine üstün tutarken kullanılır.",
    "hardly had": "💡 DERS NOTU: 'Daha yeni yapmıştım ki...' anlamına gelen devrik (Inversion) bir yapıdır.",
    "providing that": "💡 DERS NOTU: 'Şartıyla / Koşuluyla' anlamına gelen güçlü bir bağlaçtır.",
    "had i known": "💡 DERS NOTU: Üçüncü tip koşul cümlesinin (Type 3) devrik yapısıdır. (If I had known)."
}

# KELİME REHBERİ (WORD RIDDLE)
KELIME_REHBERI = [
    {"w": "kitchen", "note": "💡 NOT: 'Kitchen' (Mutfak) gibi oda isimlerinde 'in' edatı kullanılır."},
    {"w": "airplane", "note": "💡 NOT: Hava taşıtlarında 'by airplane' veya 'on the plane' diyebilirsin."},
    {"w": "doctor", "note": "💡 NOT: Mesleklerden önce 'a/an' gelir: 'I am A doctor'."},
    {"w": "thirsty", "note": "💡 NOT: 'Thirsty' (Susamak) ile 'Thirty' (30) karıştırılmamalıdır."},
    {"w": "beautiful", "note": "💡 NOT: Bu kelime 'full' ekiyle biter ama tek 'l' ile yazılır."},
    {"w": "expensive", "note": "💡 NOT: 'Cheap' (Ucuz) kelimesinin zıttıdır."},
    {"w": "tomorrow", "note": "💡 NOT: Gelecek zaman bildirir, 'tomorrow'da çift 'r' vardır."},
    {"w": "bicycle", "note": "💡 NOT: 'Cycle' (Döngü/Tur) kökünden gelir."},
    {"w": "breakfast", "note": "💡 NOT: 'Break' (Kırmak) ve 'Fast' (Oruç) kelimelerinin birleşimidir."}
]

# ==========================================
# BÖLÜM 2: YARDIMCI FONKSİYONLAR (CORE LOGIC)
# ==========================================

def temizle(metin):
    """Metni temizler, kısaltmaları açar ve karşılaştırmaya hazır hale getirir."""
    if not metin: return ""
    metin = metin.lower().strip()
    
    # Yaygın kısaltmaları normalize et
    kisaltmalar = {
        "i'm": "i am", "you're": "you are", "he's": "he is", "she's": "she is",
        "it's": "it is", "we're": "we are", "they're": "they are",
        "i've": "i have", "you've": "you have", "we've": "we have", "they've": "they have",
        "don't": "do not", "doesn't": "does not", "didn't": "did not",
        "can't": "cannot", "won't": "will not", "isn't": "is not", "aren't": "are not",
        "wouldn't": "would not", "couldn't": "could not", "shouldn't": "should not"
    }
    for k, v in kisaltmalar.items():
        metin = metin.replace(k, v)
    
    # Noktalama işaretlerini kaldır
    metin = metin.translate(str.maketrans('', '', string.punctuation))
    return metin

def benzerlik_kontrol(tahmin, dogru):
    """İki metin arasındaki benzerlik oranını döner (0.0 - 1.0 arası)."""
    return difflib.SequenceMatcher(None, temizle(tahmin), temizle(dogru)).ratio()

def hata_vurgula(tahmin, dogru):
    """Hatalı kelimeleri bulur ve HTML formatında gösterir (Streamlit için)."""
    tahmin_kelimeler = tahmin.split()
    dogru_kelimeler = dogru.split()
    vurgulu_sonuc = []
    
    for i in range(len(tahmin_kelimeler)):
        if i < len(dogru_kelimeler):
            if benzerlik_kontrol(tahmin_kelimeler[i], dogru_kelimeler[i]) > 0.8:
                vurgulu_sonuc.append(f"<span style='color:green'>{tahmin_kelimeler[i]}</span>")
            else:
                vurgulu_sonuc.append(f"<span style='color:red; text-decoration: underline'>[{tahmin_kelimeler[i].upper()}]</span>")
        else:
            vurgulu_sonuc.append(f"<span style='color:red'>[{tahmin_kelimeler[i].upper()}]</span>")
            
    return " ".join(vurgulu_sonuc)

def detayli_analiz(tahmin, dogru):
    """Kullanıcıya hatasının sebebini söyleyen akıllı fonksiyon."""
    t_temiz = temizle(tahmin)
    d_temiz = temizle(dogru)
    t_kelime = t_temiz.split()
    d_kelime = d_temiz.split()
    
    analizler = []
    
    # Kelime sayısı kontrolü
    if abs(len(t_kelime) - len(d_kelime)) > 2:
        analizler.append("⚠️ Cümle uzunluğu çok farklı. Kelime atlamış olabilirsin.")
    
    # Sıralama kontrolü
    ortak_kelimeler = set(t_kelime) & set(d_kelime)
    if len(d_kelime) > 0 and len(ortak_kelimeler) / len(d_kelime) > 0.8 and t_temiz != d_temiz:
        analizler.append("⚠️ Kelimelerin çoğu doğru ama SIRALAMA hatalı görünüyor.")
        
    # Özne-Yüklem uyumu (He/She/It özelinde)
    if any(x in d_temiz for x in ["he ", "she ", "it "]) and "don't" in t_temiz:
        analizler.append("⚠️ Dikkat: He/She/It özneleriyle 'doesn't' kullanılır.")

    if not analizler:
        analizler.append("⚠️ Harf hatası veya yanlış kelime kullanımı tespit ettim.")
    return analizler

def ders_notu_getir(cumle):
    """Cümlenin içinde geçen anahtar kelimeye göre ders notu döner."""
    cumle_lower = cumle.lower()
    for anahtar, not_metni in GRAMMAR_TIPS.items():
        if anahtar in cumle_lower: return not_metni
    return None

def kelime_karistir(cumle):
    kelimeler = cumle.split()
    random.shuffle(kelimeler)
    return " / ".join(kelimeler)

# ==========================================
# BÖLÜM 3: STREAMLIT ARAYÜZ (UI)
# ==========================================

# Yan Menü (Sidebar)
st.sidebar.title("🎮 İngilizce Koçu")
menu = st.sidebar.radio("Menü", ["Cümle Kurma", "Kelime Bilmecesi"])
st.sidebar.write(f"📊 **Toplam Puan: {st.session_state.skor}**")

# 1. MOD: CÜMLE KURMA OYUNU
if menu == "Cümle Kurma":
    st.header("📝 Cümle Kurma Oyunu")
    
    # Seviye Seçimi
    seviye = st.selectbox("Seviye Seçiniz:", ["A1", "A2", "B1", "B2"])
    
    # Soru Getirme Butonu
    if st.button("Yeni Soru Getir"):
        st.session_state.soru = random.choice(SENTENCES[seviye])
        st.session_state.cevap_verildi = False
        st.session_state.ipucu_sayisi = 0
        st.rerun()

    # Eğer bir soru varsa göster
    if st.session_state.soru:
        soru = st.session_state.soru
        dogru_cevap = soru["eng"]
        anlam = soru["tr"]
        karisik = kelime_karistir(dogru_cevap)
        
        st.info(f"**Türkçe:** {anlam}")
        st.caption(f"Karışık İpucu: {karisik}")
        
        tahmin = st.text_input("İngilizcesi nedir?")
        
        col1, col2 = st.columns(2)
        
        if col1.button("Kontrol Et"):
            oran = benzerlik_kontrol(tahmin, dogru_cevap)
            
            if oran >= 0.85:
                st.success(f"✅ TEBRİKLER! ({dogru_cevap})")
                if not st.session_state.cevap_verildi:
                    st.session_state.skor += 10
                    st.session_state.cevap_verildi = True
                
                notu = ders_notu_getir(dogru_cevap)
                if notu: st.warning(notu)
                
            else:
                st.error("🚫 HATA VAR!")
                # HTML formatında hatayı göster
                st.markdown(hata_vurgula(tahmin, dogru_cevap), unsafe_allow_html=True)
                
                # Detaylı analizleri göster
                for analiz in detayli_analiz(tahmin, dogru_cevap):
                    st.write(analiz)

        if col2.button("İpucu Al (-2 Puan)"):
            st.session_state.ipucu_sayisi = st.session_state.get('ipucu_sayisi', 0) + 1
            kelimeler = dogru_cevap.split()
            gosterilecek = " ".join(kelimeler[:st.session_state.ipucu_sayisi])
            st.warning(f"💡 İPUCU: {gosterilecek} ...")
            if not st.session_state.cevap_verildi:
                 st.session_state.skor -= 2

# 2. MOD: KELİME BİLMECE OYUNU (Word Riddle)
elif menu == "Kelime Bilmecesi":
    st.header("🧩 Kelime Bilmecesi")
    
    if st.button("Yeni Kelime Çek"):
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
        
        st.subheader(f"Karışık: {soru_data['karisik']}")
        st.write(f"İpucu: {soru_data['bosluklu']}")
        
        k_tahmin = st.text_input("Bu kelime nedir?").lower().strip()
        
        if st.button("Kelimeyi Kontrol Et"):
            if k_tahmin == soru_data["w"]:
                st.success(f"🎉 BİNGO! Doğru kelime: {soru_data['w'].upper()}")
                st.info(soru_data["note"])
                if not st.session_state.kelime_cevap_verildi:
                    st.session_state.skor += 15
                    st.session_state.kelime_cevap_verildi = True
            else:
                st.error("❌ Yanlış, tekrar dene!")
