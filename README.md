# 🚀 Rocket League Alpha Boost Engine (Pure Audio Edition)

[English](#english) - [Türkçe](#türkçe)

---

## English

### 🛡️ Easy Anti-Cheat (EAC) Security
Like most people, I am someone who cares about account security.
With the introduction of the new **Easy Anti-Cheat (EAC)** system in Rocket League, tools like `BakkesMod` have become impossible to use.

### 📝 About the Project
This project is an intelligent audio engine that simulates the Alpha Boost sound using dynamic physics calculations.

### ⛔️ The End of Alpha Boost (Gold Rush)...
The use of the legendary Alpha Boost (Gold Rush) among players has unfortunately been restricted due to these circumstances. Many players are frustrated and forced to use similar-sounding boosts to capture the Alpha Boost feel. I developed this program to bring that iconic Alpha Boost experience back to life through a safe and external method. In the following sections, you can find detailed information about the technical operation and advantages of the system.

✅ **Why is this Program 100% Safe?**
- **No Memory Reading:** Unlike other tools, this program **never** touches Rocket League's RAM (memory).
- **Pixel Analysis Only:** It works just like a human eye. It only looks at the pixels of your boost meter to decide when the sound should play.
- **External Engine:** The audio engine runs completely independently of the game process.
- **I Use It Personally:** I use this program on my main account. You can use it with complete peace of mind.

---

> **Important Note:** This is an external audio simulator. Since we cannot interfere with the game's internal code, do not expect 100% perfect synchronization like in BakkesMod. Our goal is to provide the Alpha Boost feel as a professional audio layer.

### 🎥 Video
You can better understand how the program works and how the sounds are produced by examining the example videos. You can use any boost you want in-game!

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

### 🚀 How to Install?

#### 📦 Method 1: Direct Download (More Practical)
You can quickly and practically install the program by following these **"3 Steps + Calibration"**:

1. Go to the **[Releases](https://github.com/trznx/Rocket_League-Alpha_Boost/releases)** page.
2. Download the `AlphaBoostEngine.exe` file.
3. Create a folder with any name you like on your desktop. Then move the `AlphaBoostEngine.exe` file into the folder and run it.
4. Follow the **Calibration** steps on the opened interface to complete the setup.

#### 🎯 How to Calibrate?
1. Enter **Freeplay** mode and set your **Boost** value to exactly **0**.
2. Make sure your `Settings` > `Video` > `Display Mode` is set to **Borderless** or **Full Screen**.
3. Click the **Run Calibration** button on the interface and return to your game screen before the 5-second countdown ends.
> 3.1. If you are using **Method 2**, start the calibration via `python kalibrasyon.py`.
4. A screenshot will be taken after the countdown ends. You can see this screenshot by hovering your mouse cursor over the `.exe` file on your taskbar.
5. Make the screenshot full screen and carefully select the area that neatly covers the **0** digit in your **Boost** bar.
6. Complete the process by pressing the Enter or Space key.

‼️ **Note 1:** If your Alpha Boost sound doesn't work after all steps, close and restart `AlphaBoostEngine.exe`.

‼️ **Note 2:** If I release new versions in the future, simply downloading the latest `.exe` file and replacing the old one will be enough.

⚠️ **WARNING 1:** Remember that all your files must be in the same folder.

⚠️ **WARNING 2:** Do not change your `Settings` > `Interface` > `Interface Scale & Display Scale` values after calibration. If you change your **Interface Scale** or **Display Scale** after calibrating, you may have to recalibrate. The program may not be able to correctly check your **Boost** status.

⚠️ **WARNING 3:** Your **Boost** bar must be visible for the program to work correctly.

---

#### 🐍 Method 2: Python (For Developers)
1. Install Python.
2. Run the `pip install -r requirements.txt` command.
3. Start with `python main.py`.

---

### 📌 A Few Small Notes

- **Training Mode (Unlimited Boost):** While in training mode (if unlimited boost is enabled), you should set the `Freeplay Mode` to `Enabled` on the interface or quickly press `F4` to toggle between `Enabled/Disabled` states. This setting is important to prevent incorrect boost sounds.
- **In-Game Status:** When entering online (Casual, Ranked) or offline matches (i.e., all situations where you cannot have unlimited boost), you should set `Freeplay Mode` to `Disabled` or quickly press `F4` to switch to this mode to avoid audio issues.

---

### 👥 Profiles

- **Classic Original Sound:** The boost sound at your car's maximum speed is heard at normal volume.
- **Quiet Loop Sound (Recommended):** The boost sound at your car's maximum speed is heard at a lower volume level. This way, you can prevent desync issues.
- **Low-RPM Start Sound:** The boost sound does not change according to your car's speed and is always heard the same way.

‼️ **Note:** These profiles may vary from person to person, so it may be a more logical choice to try all profiles and use the one that suits you best.

❓ **Information:** Since we cannot directly access speed data due to EAC restrictions, we estimate vehicle speed using mathematical models. This situation can lead to short-term synchronization differences between audio and visuals, especially during sudden decelerations (collisions, etc.). However, you will easily get used to this dynamic structure within a few matches.

> Getting used to this sound can take a few hours or a few matches. Once you get used to it, you will be able to use it comfortably.

---

### 💡 Recommendations from the Developer
- **In-Game Settings:** Use `Standard Boost` or select any boost you want and turn on the `Use Standard Boost Sound` feature in `Settings` -> `Audio`.
- **Volume Balance:** Lower in-game sounds or increase the **Alpha Boost** volume from the program's interface so that in-game sounds do not drown out the **Alpha Boost** sound.
- **Delay:** For smoother Alpha Boost usage, set the `Audio Start Delay` to `0ms` (the default value). If this is not suitable for you, you can choose the most appropriate delay value by personally testing delay values in training mode.
- **Tips:** Be sure to read the "Tips & Info" section on the interface.

### 🛠️ Developer's Method (My Personal Method)
- For the most realistic feel, I recommend keeping the Alpha Boost volume level between **20%-35% (variable)** on the interface and playing light music in the background. The music naturally masks the very small software-generated synchronization differences, perfectly simulating the BakkesMod feel. You can optimize the volume level according to your own Windows/Game settings. However, hearing the sound as a **background layer** will significantly increase the realism of the experience.

- If you want the exact original Alpha Boost mechanics in-game and feel that this program will not meet your expectations, the method I described above will be very helpful. Hearing the Alpha Boost sound faintly will perfectly create the "I'm really using Alpha Boost!" feeling in you.

---

### 📜 License
This project is protected by the **MIT License**.
You are completely free to develop, improve, and share this project. We encourage the community to make better versions! However, since it is based on this original work, all improvements must maintain this license and credit the original project.


---
---

## Türkçe

### 🛡️ Easy Anti-Cheat (EAC) Güvenliği
Ben de diğer çoğu insan gibi hesap güvenliğini düşünenlerdenim.
Rocket League'e yeni gelen bir sistem olan **Easy Anti-Cheat (EAC)** ile birlikte `BakkesMod` gibi araçların kullanımı artık imkânsız hâle geldi.

### 📝 Proje Hakkında
Bu proje, Alpha Boost sesini dinamik fizik hesaplamalarıyla simüle eden akıllı bir ses motorudur.

### ⛔️ Alpha Boost (Gold Rush) Sonu...
Oyuncular arasında efsaneleşen Alpha Boost (Gold Rush) kullanımı ne yazık ki bu durumlardan ötürü kısıtlanmış oldu. Birçok oyuncu bu durumdan şikayetçi ve Alpha Boost hissiyatını yakalayabilmek için benzer sesli boostlar (takviyeler) kullanmak zorunda kalıyorlar. Bu programı, Alpha Boost'un o ikonik deneyimini güvenli ve harici bir yöntemle yeniden hayata döndürmek için geliştirdim. Aşağıdaki bölümlerde, sistemin teknik işleyişi ve sunduğu avantajlar hakkında detaylı bilgi edinebilirsiniz.

✅ **Bu Program Neden %100 Güvenli?**
- **Hafıza Okumaz:** Diğer araçların aksine, bu program Rocket League'in RAM'ine (hafızasına) **asla** dokunmaz.
- **Sadece Piksel Analizi:** Tıpkı bir insan gözü gibi çalışır. Sadece boost (takviye) sayacınızdaki piksellere bakarak sesin ne zaman çalacağına karar verir.
- **Harici Motor:** Ses motoru oyun sürecinden tamamen bağımsız çalışır.
- **Bizzat Kullanıyorum:** Ben (geliştirici) bu programı kendi ana hesabımda kullanıyorum. Tamamen gönül rahatlığıyla kullanabilirsiniz.

---

> **Önemli Not:** Bu harici bir ses simülatörüdür. Oyunun iç koduna müdahale edemediğimiz için BakkesMod'daki gibi %100 kusursuz bir senkronizasyon beklememelisiniz. Amacımız, profesyonel bir ses katmanı olarak Alpha Boost hissiyatını yaşatmaktır.

### 🎥 Video
Örnek videoları inceleyerek programın nasıl çalıştığını ve seslerin nasıl çıktığını daha rahat bir şekilde anlayabilirsiniz. Oyun içerisinde, istediğiniz boostu kullanabilirsiniz! 

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

#### 📦 Yöntem 1: Doğrudan İndirme (Daha Pratik)
Hızlı ve pratik bir şekilde aşağıdaki **"3 Adım + Kalibrasyon"** aşamalarını takip ederek programı kurabilirsiniz:

1. **[Releases](https://github.com/trznx/Rocket_League-Alpha_Boost/releases)** sayfasına gidin.
2. `AlphaBoostEngine.exe` dosyasını indirin.
3. Masaüstünüzde istediğiniz isme sahip bir klasör oluşturun. Ardından `AlphaBoostEngine.exe` dosyasını klasörün içerisine atın ve bu dosyayı çalıştırın.
4. Açılan arayüzde **Kalibrasyon** adımlarını uygulayın ve kurulumu tamamlayın.

#### 🎯 Kalibrasyon Nasıl Yapılır?
1. **Serbest Oyun** moduna girin ve **Boost** değerinizi tam olarak **0** yapın.
2. `Ayarlar` > `Görüntü` > `Ekran Modu` kısmının **Sınırsız** veya **Tam Ekran** olduğundan emin olun.
3. Arayüzdeki **Run Calibration** butonuna tıklayın ve 5 saniyelik geri sayım bitmeden oyun ekranınıza dönün.
> 3.1. Eğer **Yöntem 2**'yi kullanıyorsanız `python kalibrasyon.py` üzerinden kalibrasyonu başlatın.
4. Geri sayım bittikten sonra bir ekran görüntüsü alınacaktır. Bu ekran görüntüsünü görev çubuğunuzdaki `.exe` dosyasının üzerine fare imleciniz ile gelerek görebilirsiniz.
5. Ekran görüntüsünü tam ekran yapın ve **Boost** barınızdaki **0** rakamını düzgünce kapsayacak bir şekilde seçim yapın.
6. Enter veya Space tuşuna basarak işlemi tamamlayın.

‼️ **Not 1:** Tüm işlemler bittikten sonra Alpha Boost sesiniz çalışmazsa `AlphaBoostEngine.exe` dosyasını kapatıp tekrardan çalıştırın.

‼️ **Not 2:** Eğer ilerleyen zamanlarda yeni sürümler yayımlarsam yalnızca son sürümdeki `.exe` dosyasını indirip eski `.exe` dosyası ile değiştirmeniz yeterli olacaktır.

⚠️ **UYARI 1:** Tüm dosyalarınızın aynı klasörün içerisinde olması gerektiğini unutmayın.

⚠️ **UYARI 2:** Kalibrasyon yaptıktan sonra `Ayarlar` > `Arayüz` > `Arayüz Ölçeği & Ekran Ölçeği` değerlerini asla değiştirmeyin (değiştirip eski hâline getirme işlemini bile yapmayın). Eğer **Arayüz Ölçeği** veya **Ekran Ölçeği** değerlerinizi kalibrasyon işlemi yaptıktan sonra değiştirirseniz `tekrardan` kalibrasyon yapmak zorunda kalabilirsiniz. Çünkü program düzgün bir şekilde **Boost (Takviye)** durumunuzu kontrol edemeyebilir ve bundan dolayı **Boost (Takviye)** değeriniz **0** olsa bile **Boost** basmaya çalıştığınızda ses duyabilirsiniz.

⚠️ **UYARI 3:** Programın düzgün bir şekilde çalışabilmesi için **Boost (Takviye)** barınızın `kesinlikle` görünür olması şarttır.

---

#### 🐍 Yöntem 2: Python (Geliştiriciler için)
1. Python yükleyin.
2. `pip install -r requirements.txt` komutunu çalıştırın.
3. `python main.py` ile başlatın.

---

### 📌 Küçük Birkaç Not

- **Antrenman Modu (Sınırsız Boost):** Antrenman modundayken (sınırsız boost özelliğiniz açıksa) arayüz üzerinden `Freeplay Mode` kısmını `Enabled` durumuna getirmelisiniz veya hızlıca `F4` tuşuna basarak da `Enabled/Disabled` durumları arasında geçiş yapabilirsiniz. Bu ayarın önemi, boost sesinin hatalı gelmesini önlemek içindir.
- **Oyun İçi Durum:** Çevrim içi (Normal, Dereceli) veya çevrim dışı maç girerken (yani sınırsız boost özelliğinizin olamayacağı tüm durumlarda) ses sorunu yaşamamanız için `Freeplay Mode` kısmını `Disabled` durumuna getirmelisiniz veya hızlıca `F4` tuşuna basarak da bu duruma getirebilirsiniz.

---

### 👥 Profiller 

- **Classic Original Sound:** Arabanızın maksimum hızındaki boost sesi normal seste duyulur.
- **Quiet Loop Sound (Recommended):** Arabanızın maksimum hızındaki boost sesi daha düşük bir ses seviyesinde duyulur. Bu sayede senkronize olmama durumunun önüne geçebilirsiniz.
- **Low-RPM Start Sound:** Boost sesi arabanızın hızına göre değişiklik göstermez ve hep aynı şekilde duyulur.

‼️ **Not:** Bu profiller kişiden kişiye değişiklik gösterebilir, bu yüzden tüm profilleri deneyerek kendinize en çok uyan profili kullanmanız daha mantıklı bir seçim olabilir.

❓ **Bilgilendirme:** EAC kısıtlamaları nedeniyle hız verisine doğrudan erişemediğimiz için araç hızını matematiksel modellerle tahmin ediyoruz. Bu durum, özellikle ani yavaşlamalarda (çarpışma vb.) ses ile görsel arasında kısa süreli senkronizasyon farklarına yol açabilir. Ancak bu dinamik yapıya birkaç maç içerisinde kolayca alışılmaktadır.

> Bu sese alışmanız birkaç saat veya birkaç maç sürebilir. Alıştıktan sonra rahatlıkla kullanabileceksiniz.

---

  ### 💡 Geliştirici'den Tavsiyeler
- **Oyun İçi Ayarlar:** `Standart Boost` kullanın ya da istediğiniz bir boostu seçip `Ayarlar` -> `Ses` kısmından `Standart Boost Sesini Kullan` özelliğini açın.
- **Ses Dengesi:** Oyun içi sesleri kısın veya programın arayüzünden **Alpha Boost** sesini artırın ki oyun içi sesler **Alpha Boost** sesini bastırmasın.
- **Gecikme:** Daha düzgün bir Alpha Boost kullanımı için `Audio Start Delay` ayarını `0ms` yani varsayılan değer olarak ayarlayın. Eğer bu durum size uygun değilse antrenman modunda bizzat gecikme değerlerini deneyerek size en uygun olan gecikme değerini seçebilirsiniz.
- **İpuçları:** Arayüzdeki "Tips & Info" kısmını mutlaka okuyun.

### 🛠️ Geliştirici'nin Yöntemi (Benim Şahsi Yöntemim)
- En gerçekçi hissiyat için Alpha Boost ses seviyesini arayüz üzerinden **%20-%35 (değiştirilebilir)** aralığında tutmanızı ve arkada hafif bir müzik açmanızı öneririm. Müzik, yazılımsal olarak oluşan çok küçük senkronizasyon farklarını doğal bir şekilde maskeleyerek BakkesMod hissiyatını mükemmel şekilde simüle eder. Ses seviyesini kendi Windows/Oyun ayarlarınıza göre optimize edebilirsiniz. Ancak sesi bir **arka plan katmanı** gibi duymak deneyimin gerçekçiliğini önemli ölçüde artıracaktır.

- Eğer oyundaki orijinal Alpha Boost mekaniğini birebir istiyorsanız ve bu program sizin beklentilerinizi karşılamayacak gibi hissettiriyorsa yukarıda anlattığım yöntem çok işinize yarayacaktır. Alpha Boost sesini hafiften duymanız "Gerçekten Alpha Boost kullanıyorum!" hissini sizde mükemmel bir şekilde oluşturacaktır.

---

### 📜 Lisans
Bu proje **MIT Lisansı** ile korunmaktadır.
Bu projeyi geliştirmekte, iyileştirmekte ve paylaşmakta tamamen özgürsünüz. Topluluğun daha iyi sürümler yapmasını teşvik ediyoruz! Ancak, bu orijinal çalışmayı temel aldığı için, yapılan tüm geliştirmelerin bu lisansı koruması ve orijinal projeye atıfta bulunması zorunludur.
