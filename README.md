# 🚀 Rocket League Alpha Boost Engine (Pure Audio Edition)

[English](#english) - [Türkçe](#türkçe)

---

## English

### 🛡️ Anti-Cheat (EAC) Security
**Your account safety is our top priority.**
With Rocket League's new **Easy Anti-Cheat (EAC)** system, the use of tools like BakkesMod has become impossible.

### 📝 About the Project
This project is an intelligent audio engine that simulates Alpha Boost sounds using dynamic physics calculations.

Due to the **Easy Anti-Cheat (EAC)** system, the incredibly popular Alpha Boost (Gold Rush) has also become unavailable. Like many players, I was frustrated by not being able to use this boost. Many players started using boosts that sound most similar to Alpha Boost. This is why I decided to create this program. In the following sections, you will find much more information about the program.

**Why is this program 100% Safe?**
- **No Memory Reading:** Unlike other tools, this program **never** touches Rocket League's RAM (Memory).
- **Pixel Analysis Only:** It works exactly like a human eye. It only looks at the pixels of your boost meter to decide when to play the sound.
- **External Engine:** The audio engine runs completely independently of the game process.
- **I Use It Personally:** I (the developer) use this program on my main account. You can use it with complete peace of mind.

---

> **Important Note:** This is an external audio simulator. Since we cannot interfere with the game's internal code, you should not expect 100% perfect synchronization like in BakkesMod. Our goal is to provide the Alpha Boost feel as a professional audio layer.

### 🎥 Video
Explore how the program operates via these demo videos. You can review the configuration settings by interacting with the on-screen interface, and it works seamlessly regardless of which boost is selected in-game.

<p align="center">
  <video src="https://github.com/user-attachments/assets/04fc5710-dfd4-4759-b48b-f19e51296ce9" width="100%" controls>
    Your browser does not support the video tag.
  </video>
</p>
<p align="center">
  <video src="https://github.com/user-attachments/assets/9ba79b13-ad12-4ebb-ba3b-052724cee48c" width="100%" controls>
    Your browser does not support the video tag.
  </video>
</p>
<p align="center">
  <video src="https://github.com/user-attachments/assets/7a223084-ec5d-46bb-8aee-e0f501a05463" width="100%" controls>
    Your browser does not support the video tag.
  </video>
</p>

---

### ⚙️ Installation & Preparation

#### 📦 Option 1: Direct Download (For Beginners)
If you don't want to deal with Python, you can directly download the compiled version:
1. Go to the **[Releases](https://github.com/your-repo/releases)** page.
2. Download the `AlphaBoostEngine.exe` file.
3. Run the `.exe` file and follow the calibration step.

#### 🐍 Option 2: Python (For Developers)
1. Install Python.
2. Run the `pip install -r requirements.txt` command.
3. Start with `python main.py`.

#### 🎯 Calibration (Mandatory - To be done once)
1. Enter **Freeplay** mode.
2. Set your boost exactly to **0**.
3. Ensure the game is in **Borderless** or **Windowed** mode. (Full Screen mode works too; I personally did it in full screen mode)
4. Start calibration by clicking the calibration button on the interface or via `python kalibrasyon.py`.
5. **⚠️ CRITICAL WARNING:** Do not change your **Interface Scale** after calibration! For example, if you calibrate while your Rocket League interface is at 100% scale and later drop it to 30% or another value, the program may not work correctly. If you change the scale, you must **re-calibrate**.
6. **⚠️ Visibility:** The boost bar **must** be visible for the program to work correctly. If the boost bar is hidden, the sound will not trigger, meaning the program cannot function properly.

---

### 📌 Notes

- **Training Mode (Unlimited Boost):** While in training mode (if unlimited boost is enabled), you should set **Freeplay Mode** to **Enabled** in the UI or quickly press **F4** to toggle between Enabled/Disabled states. This setting is important to prevent incorrect boost sounds.
- **In-Game:** When entering online (Casual, Ranked) or offline matches (i.e., all situations where you don't have unlimited boost), you should set **Freeplay Mode** to **Disabled** or quickly press **F4** to switch to this mode to avoid audio issues.
- **Classic Original Sound:** If you select this profile, your boost sound at SuperSonic speed will be heard at normal volume.
- **Quiet Loop Sound (Recommended):** If you select this profile, your boost sound at SuperSonic speed will be heard at a lower volume. This way, you can help mitigate perceived desync. It depends entirely on your personal preference.
- **Low-RPM Start Sound:** If you select this profile, your boost sound will not change according to your car's speed and will always be heard at the same pitch.

**Information:** Since we cannot see your car's speed directly (due to EAC), we estimate it mathematically and speed up/slow down your boost sound accordingly. This can lead to audio mismatches, but you'll get used to it quickly. For example, if you boost for a long time and then suddenly make a move that slows your car down, our program might still think you're fast and change the boost sound accordingly. This is exactly why audio mismatches can occur.

> It might take a couple of hours or a few matches to familiarize yourself with the audio. Once you've adjusted, you'll be able to use it comfortably.

### 💡 Developer Recommendations
- **In-Game Settings:** Use **Standard Boost** or select any boost you want and turn on the **"Use Standard Boost Sound"** feature in **Settings -> Audio**. (Using the Standard Boost sound will be more effective and is recommended)
- **Volume Balance:** Lower in-game sounds or increase the Alpha Boost volume from the program's interface so that in-game sounds do not drown out the Alpha Boost sound.
- **Profiles:** I recommend using the **"Quiet Loop Sound (Recommended)"** profile. You can also try other profiles and use whichever suits you best.
- **Delay:** For smoother Alpha Boost usage, keep the **Audio Start Delay** setting at **0ms**. If this is not suitable for you, you can choose the most appropriate delay value by making changes through the interface and trying it in training mode.
- **Tips:** Be sure to read the "Tips & Info" section on the interface.

### 🛠️ Developer's Method (My Personal Method)
I almost always listen to music in the background while playing. I set the Alpha Boost volume on the interface between **20%-35%** (above 30% if music is playing). (The reason for my volume level being this way is due to my computer volume and game volume levels. It would be better if you determine a custom volume level for yourself)
**Why?** This method perfectly "masks" the minor synchronization differences and the original Alpha Boost sound. Hearing the Alpha Boost as a background layer makes it feel as if BakkesMod is actually there and you're using Alpha Boost. It provides an incredibly realistic experience when combined with music! (You don't have to turn on music, but my experience creates a much more effective result. People who can distinguish between the original Alpha Boost sound and the Alpha Boost sound provided in our program MAY be bothered by this situation; that's why I gave such a recommendation)

---

### 📜 License
This project is protected by the **MIT License**.
You are completely free to develop, improve, and share this project. We encourage the community to make better versions! However, since it is based on this original work, all improvements must maintain this license and credit the original project.

---
---

## Türkçe

### 🛡️ Anti-Cheat (EAC) Güvenliği
**Hesap güvenliğiniz bizim birinci önceliğimizdir.**
Rocket League'in yeni **Easy Anti-Cheat (EAC)** sistemiyle birlikte, BakkesMod gibi araçların kullanımı artık imkansız hâle geldi.

### 📝 Proje Hakkında
Bu proje, Alpha Boost seslerini dinamik fizik hesaplamalarıyla simüle eden akıllı bir ses motorudur.

**Easy Anti-Cheat (EAC)** sistemi yüzünden oyuncular arasında inanılmaz popüler olan Alpha Boost (Gold Rush) da kullanılamaz hâle geldi.
Benim gibi birçok oyuncu, bu boostu kullanamadığı için şikayetçi. Birçok oyuncu da Alpha Boost sesine en çok benzeyen boostlar kullanmaya başladı.
Ben de bu sebepten ötürü böyle bir program yapma kararı aldım. Bu metnin devamında program ile ilgili çok daha fazla bilgiye sahip olacaksınız.


**Bu Program Neden %100 Güvenli?**
- **Hafıza Okumaz:** Diğer araçların aksine, bu program Rocket League'in RAM'ine (hafızasına) **asla** dokunmaz.
- **Sadece Piksel Analizi:** Tıpkı bir insan gözü gibi çalışır. Sadece boost (takviye) sayacınızdaki piksellere bakarak sesin ne zaman çalacağına karar verir.
- **Harici Motor:** Ses motoru oyun sürecinden tamamen bağımsız çalışır.
- **Bizzat Kullanıyorum:** Ben (geliştirici) bu programı kendi ana hesabımda kullanıyorum. Tamamen gönül rahatlığıyla kullanabilirsiniz.

---

> **Önemli Not:** Bu harici bir ses simülatörüdür. Oyunun iç koduna müdahale edemediğimiz için BakkesMod'daki gibi %100 kusursuz bir senkronizasyon beklememelisiniz. Amacımız, profesyonel bir ses katmanı olarak Alpha Boost hissiyatını yaşatmaktır.

### 🎥 Video
Örnek videolar üzerinden programın nasıl çalıştığını daha iyi anlayın. Video üzerindeki arayüzü kontrol ederek ayar yapılandırmalarını inceleyebilirsiniz, seçilen boost fark etmeksizin kullanabilirsiniz.

<p align="center">
  <video src="https://github.com/user-attachments/assets/04fc5710-dfd4-4759-b48b-f19e51296ce9" width="100%" controls>
    Tarayıcınız video etiketini desteklemiyor.
  </video>
</p>
<p align="center">
  <video src="https://github.com/user-attachments/assets/9ba79b13-ad12-4ebb-ba3b-052724cee48c" width="100%" controls>
    Tarayıcınız video etiketini desteklemiyor.
  </video>
</p>
<p align="center">
  <video src="https://github.com/user-attachments/assets/7a223084-ec5d-46bb-8aee-e0f501a05463" width="100%" controls>
    Tarayıcınız video etiketini desteklemiyor.
  </video>
</p>

---

### ⚙️ Kurulum ve Hazırlık

#### 📦 Yöntem 1: Doğrudan İndirme (Yeni Başlayanlar için)
Python ile uğraşmak istemiyorsanız direkt derlenmiş sürümü indirebilirsiniz:
1. **[Releases](https://github.com/your-repo/releases)** sayfasına gidin.
2. `AlphaBoostEngine.exe` dosyasını indirin.
3. `.exe` dosyasını çalıştırın ve kalibrasyon adımını takip edin.

#### 🐍 Yöntem 2: Python (Geliştiriciler için)
1. Python yükleyin.
2. `pip install -r requirements.txt` komutunu çalıştırın.
3. `python main.py` ile başlatın.

#### 🎯 Kalibrasyon (Zorunlu - 1 Kez Yapılacak)
1. **Freeplay** moduna girin.
2. Boostunuzu tam **0** yapın.
3. Oyunun **Sınırsız Pencere** veya **Pencereli** modda olduğundan emin olun. (Tam Ekran modunda da olur, ben tam ekran modunda yapmıştım)
4. Arayüz üzerindeki kalibrasyon butonuna tıklayarak **VEYA** `python kalibrasyon.py` üzerinden kalibrasyonu başlatın.
5. **⚠️ KRİTİK UYARI:** Kalibrasyon yaptıktan sonra **Arayüz Ölçeğini (Interface Scale)** değiştirmeyin! Örneğin Rocket League ayarlarınızdaki arayüzünüz %100 ölçekteyken kalibrasyon yapıp daha sonrasında %30'a veya başka bir değere düşürürseniz program düzgün çalışmayabilir. Ölçek değiştirirseniz **tekrardan** kalibrasyon yapmalısınız.
6. **⚠️ Görünürlük:** Programın çalışması için boost (takviye) barının **görünür** olması şarttır. Boost barı gizliyken ses tetiklenmez yani program düzgün bir şekilde çalışamaz.

---

### 📌 Notlar

- **Antrenman Modu (Sınırsız Boost):** Antrenman modundayken (sınırsız boost özelliğiniz açıksa) arayüz üzerinden **Freeplay Mode** kısmını **Enabled** durumuna getirmelisiniz veya hızlıca F4 tuşuna basarak da Enabled/Disabled durumları arasında geçiş yapabilirsiniz. Bu ayarın önemi, boost sesinin hatalı gelmesini önlemek içindir.
- **Oyun İçi:** Çevrim içi (Normal, Dereceli) veya çevrim dışı maç girerken (yani sınırsız boost özelliğinizin olamayacağı tüm durumlarda) ses sorunu yaşamamanız için **Freeplay Mode** kısmını **Disabled** durumuna getirmelisiniz veya hızlıca F4 tuşuna basarak da bu duruma getirebilirsiniz. 
- **Classic Original Sound:** Profil olarak bu profili seçerseniz SuperSonic hızınızdaki boost sesiniz normal seste duyulur.
- **Quiet Loop Sound (Recommended):** Profil olarak bu profili seçerseniz SuperSonic hızınızdaki boost sesiniz daha az ses seviyesinde duyulur. Bu sayede senkronize olma durumunun bir diğer söyleyişle önüne geçmiş olabilirsiniz. Tamamen kendi hissiyatınıza bağlıdır.
- **Low-RPM Start Sound:** Profil olarak bu profili seçerseniz boost sesiniz arabanızın hızına göre değişiklik göstermez ve hep aynı hızda duyulur.
**Bilgilendirme:** Arabanızın hızını bizzat göremediğimiz için (EAC yüzünden) bunu matematiksel tahmin ile tahmin ederiz ve boost sesinizi buna göre hızlandırır/yavaşlatırız. Bu ses uyuşmazlığına yol açabilir ama kısa bir süre sonra alışıyorsunuz. Örneğin uzun bir süre boost basarsanız ve bir anda arabanızı yavaşlatacak bir hamle yaparsanız programımız sizi hâlâ hızlı sanıp boost sesini de ona göre değiştirebilir. İşte tam bu yüzden ses uyuşmazlığı ortaya çıkabilir.

> Bu sese alışmanız birkaç saat veya birkaç maç sürebilir. Alıştıktan sonra rahatlıkla kullanabileceksiniz.

### 💡 Geliştirici Tavsiyeleri
- **Oyun İçi Ayarlar:** **Standart Boost** kullanın ya da istediğiniz bir boostu seçip **Ayarlar -> Ses** kısmından **"Standart Boost Sesini Kullan"** özelliğini açın. (Standart Boost sesinin olması daha etkili olacaktır, tavsiye edilir)
- **Ses Dengesi:** Oyun içi sesleri kısın veya programın arayüzünden Alpha Boost sesini artırın ki oyun içi sesler Alpha Boost sesini bastırmasın.
- **Profiller:** **"Quiet Loop Sound (Recommended)"** profilini kullanmanızı tavsiye ederim. Diğer profilleri de deneyebilirsiniz, hangisi size en uygun gelirse onu kullanabilirsiniz.
- **Gecikme:** Daha düzgün bir Alpha Boost kullanımı için **Audio Start Delay** ayarını **0ms**'de tutun. Eğer bu durum size uygun değilse arayüz üzerinden değişiklikler yaparak ve antrenman modunda deneyerek size en uygun olan gecikme değerini seçebilirsiniz.
- **İpuçları:** Arayüzdeki "Tips & Info" kısmını mutlaka okuyun.

### 🛠️ Geliştirici Yöntemi (Benim Şahsi Yöntemim)
Oynarken neredeyse her zaman arkada müzik dinliyorum. Alpha Boost sesini arayüzden **%20-%35** aralıgı (müzik sesliyse %30 üzerine) ayarlıyorum. (Arayüzümdeki ses seviyesinin bu şekilde olmasının sebebi, bilgisayar sesim ve oyun sesimin ses düzeyinden kaynaklanıyor. Siz kendinize özel bir ses seviyesi belirlerseniz daha iyi olur)
**Neden?** Bu yöntem, BakkesMod olmadığı için oluşan küçük senkronizasyon farklarını ve orijinal Alpha Boost sesini mükemmel şekilde "örtbas ediyor". Alpha Boost'u bir arka plan katmanı olarak duymak, sanki gerçekten BakkesMod varmış gibi hissettiriyor. Müzikle birleştiğinde inanılmaz gerçekçi bir deneyim sunuyor! (Müzik açmak zorunda değilsiniz ama benim bu deneyimim çok daha etkili bir sonuç yaratıyor. Orijinal Alpha Boost sesi ile bizim programımızdaki sunulan Alpha Boost sesini ayırt edebilecek seviyeye sahip olan kişiler bu durumdan BELKİ rahatsız olabilirler, bu sebepten ötürü böyle bir tavsiye verdim)

---

### 📜 Lisans
Bu proje **MIT Lisansı** ile korunmaktadır.
Bu projeyi geliştirmekte, iyileştirmekte ve paylaşmakta tamamen özgürsünüz. Topluluğun daha iyi sürümler yapmasını teşvik ediyoruz! Ancak, bu orijinal çalışmayı temel aldığı için, yapılan tüm geliştirmelerin bu lisansı koruması ve orijinal projeye atıfta bulunması zorunludur.
