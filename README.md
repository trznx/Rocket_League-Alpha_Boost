# 🚀 Rocket League Alpha Boost Engine (Pure Audio Edition)

[English](#english) | [Türkçe](#türkçe)

---

## English

### 📝 About the Project
This project is an intelligent audio engine that simulates professional Alpha Boost sounds using dynamic physics calculations, without modifying the game's original files (**Anti-Cheat Safe**).

> **Important Note:** This is an external audio simulator. Since we cannot modify the game's internal code like BakkesMod does, the synchronization and audio experience won't be "1:1 perfect" like BakkesMod. It is designed to provide the Alpha Boost feel and sound as a layer over your gameplay.

### 🎥 Video Demonstration
You can see and hear how the program works in-game by watching this video:
[Watch the Demonstration Video Here](https://link-to-your-video.com)

### ⚙️ How to Use (Step-by-Step)
1. **Requirements:** Ensure you have Python installed.
2. **Install Libraries:** Open your terminal and run:
   ```cmd
   pip install -r requirements.txt
   ```
3. **Calibration (Required Once):**
   - Open Rocket League and go to **Freeplay**.
   - Use your boost until it reaches **0 (Zero)**.
   - Set the game to **Borderless** or **Windowed** mode.
   - Run `python kalibrasyon.py` from the terminal. It will automatically find the boost meter and save your settings.
4. **Running the Engine:**
   - After calibration, run `python main.py` before you start playing.
   - Use the **GUI (Interface)** to adjust volume, toggle the engine, or enable Freeplay Mode (Unlimited Boost).

### 💡 Developer Recommendations
- **Boost Choice:** It is highly recommended to use the **Standard Boost** in-game. If you are using another boost, go to **Settings -> Audio** and enable **"Use Standard Boost Sound"**.
- **Volume Balancing:** To prevent the in-game boost from drowning out the Alpha Boost, lower the in-game sound effects or increase the Alpha Boost volume via our interface.
- **Profiles:** You can choose from 3 different sound profiles in the dropdown menu. We recommend using the **"Quiet Loop Sound (Recommended)"** for the best experience.
- **Audio Delay:** Keep the **Audio Start Delay** at **0ms** for the most responsive feel. Increase it only if you feel the sound is triggering too early on your specific system.
- **Tips:** Don't forget to check the "Tips & Info" section in the interface!

### 🛠️ Developer's Method (How I Use It)
I usually listen to music in the background while playing. I set the Alpha Boost volume between **20% - 35%** in the interface. When listening to music, I prefer it above **30%** so I can still hear the boost clearly. 
The advantage of this method is that it masks the minor synchronization differences that occur because we aren't using BakkesMod. I can hear the Alpha Boost as a background layer, making it feel like I'm actually using it in BakkesMod. You can follow this method or find your own "sweet spot" using the interface.

---

## Türkçe

### 📝 Proje Hakkında
Bu proje, oyunun orijinal dosyalarını değiştirmeden (Anti-Cheat güvenli) profesyonel Alpha Boost seslerini dinamik fizik hesaplamalarıyla simüle eden akıllı bir ses motorudur.

> **Önemli Not:** Bu harici bir ses simülatörüdür. BakkesMod gibi oyunun iç koduna müdahale edemediğimiz için, BakkesMod'daki gibi %100 kusursuz bir senkronizasyon beklememelisiniz. Amacımız, oyunun üzerine bir katman olarak Alpha Boost hissiyatını ve sesini eklemektir.

### 🎥 Video Gösterimi
Programın oyun içinde nasıl göründüğünü ve duyulduğunu bu videodan izleyebilirsiniz:
[Tanıtım Videosunu Buradan İzleyin](https://link-to-your-video.com)

### ⚙️ Nasıl Kullanılır? (Adım Adım)
1. **Gereksinimler:** Bilgisayarınızda Python yüklü olduğundan emin olun.
2. **Kütüphaneleri Kurun:** Terminali açın ve şu komutu çalıştırın:
   ```cmd
   pip install -r requirements.txt
   ```
3. **Kalibrasyon (Sadece 1 Kere):**
   - Rocket League'i açın ve **Freeplay** (Antrenman) moduna girin.
   - Boostunuzu **0 (Sıfır)** olana kadar harcayın.
   - Oyunun **Sınırsız Pencere** (Borderless) veya **Pencereli** modda olduğundan emin olun.
   - Terminalden `python kalibrasyon.py` komutunu çalıştırın. Program boost göstergesini bulup ayarlarınızı kaydedecektir.
4. **Çalıştırma:**
   - Kalibrasyon bittikten sonra, oyuna başlamadan önce `python main.py` yazın.
   - Karşınıza çıkan **Arayüz (GUI)** üzerinden ses seviyesini ayarlayabilir, motoru açıp kapatabilir veya Sınırsız Boost (Freeplay) modunu aktif edebilirsiniz.

### 💡 Geliştirici Tavsiyeleri
- **Boost Seçimi:** Oyun içerisinde **Standart Boost** kullanmanız şiddetle önerilir. Başka bir boost kullanıyorsanız bile **Ayarlar -> Ses** sekmesinden **"Standart Boost Sesini Kullan"** özelliğini aktif edin.
- **Ses Dengesi:** Oyun içi boost sesinin Alpha Boost'u bastırmaması için oyun içi sesleri biraz düşürmeniz veya arayüz üzerinden Alpha Boost sesini yükseltmeniz önerilir.
- **Profiller:** Arayüzdeki 3 seçenekli menüden istediğinizi seçebilirsiniz, ancak **"Quiet Loop Sound (Recommended)"** olanı kullanmanız tavsiye edilir.
- **Ses Gecikmesi:** En iyi tepkisellik için **Audio Start Delay** ayarını **0ms**'de tutun. Eğer sesin çok erken tetiklendiğini hissederseniz kendinize göre artırabilirsiniz.
- **İpuçları:** Arayüzdeki "Tips & Info" kısmını okumayı unutmayın!

### 🛠️ Geliştirici Yöntemi (Ben Nasıl Kullanıyorum?)
Ben bu programı kullanırken genellikle arka planda şarkı dinliyorum. Alpha Boost sesini arayüzden **%20 - %35** aralığında ayarlıyorum. Şarkı dinlerken genellikle **%30** üzerine çıkıyorum ki boost sesini net duyabileyim.
Bu yöntemin avantajı, BakkesMod gibi kusursuz bir senkronizasyon beklediğimiz durumlardaki küçük farkları örtbas etmesidir. Alpha Boost sesini arkadan hafifçe duyduğumda, sanki gerçekten BakkesMod varmış gibi hissediyorum. Siz de bu şekilde yapabilir veya arayüzden kendinize en uygun ayarı bulabilirsiniz.
