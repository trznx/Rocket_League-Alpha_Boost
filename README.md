# Rocket League Alpha Boost Engine

[English](#english) | [Türkçe](#turkce)

---

<a id="english"></a>
## 🇬🇧 English

## 🎬 Preview

Before continuing, you can quickly understand what the program is by checking the video and screenshot below:

<p align="center">
  <video src="https://github.com/user-attachments/assets/8dcaedb0-ec1b-4ab3-bb69-4ab9269747d1" width="100%" controls>
    Your browser does not support the video tag.
  </video>
</p>
<img width="413" height="410" alt="image" src="https://github.com/user-attachments/assets/6c3c7bea-6a5d-45b7-82fa-0ed67bcd0b78" />


### ✨ Overview

**Alpha Boost Engine** is a desktop application built for players who want to experience the Alpha Boost sound without modifying game files or relying on different mod methods.

This program does not add the real Alpha Boost item into the game or force-unlock it. Instead, it recreates the Alpha Boost sound by using external sound files and changing them according to your car speed in-game.

---

### 🛡️ Safety

This program is designed to stay away from the areas that players worry about the most.

- It does not modify Rocket League files.
- It does not make any additional intervention to Rocket League files.
- It does not read Rocket League files.

⚪️ It works as an external audio application. In short, it is an ideal solution for players who are concerned about the **Easy Anti-Cheat** system.

---

### ❔ How It Works?

The audio engine basically combines these three conditions (API):

- Instant tracking of whether boost is being pressed,
- Checking whether the boost amount is being consumed,
- Instant monitoring of the car speed,

⚪️ By blending this data together, the program determines when the Alpha Boost sound should play and in what tone it should play according to speed. Thanks to this smart structure, unnecessary sound triggers are prevented during goal replays or when your boost amount is **0** and you still press the button.
  
---

### 👥 Profiles

You can test every profile and choose the one that suits you best.

| Profile | Description | Short Note |
| --- | --- | --- |
| `Quality` | The profile that reacts to speed in the most detailed way and has smoother transitions | Best Choice |
| `Advanced` | The profile that reacts to speed but has a higher sound level | Louder Sound |
| `Normal` | A constant profile that plays the same sound at all speeds | Simplest Use |

---

### ❇️ Installation Steps

#### 1️⃣ - Download the Program:

- Download the latest version [from here](https://github.com/trznx/Rocket_League-Alpha_Boost/releases) and place the `.exe` file on your desktop or inside any folder you want.

- Then run the `.exe` file.

#### 2️⃣ - API Configuration:

🔗 Default file path for **Steam** users:

```text
C:\Program Files (x86)\Steam\steamapps\common\rocketleague\TAGame\Config\DefaultStatsAPI.ini
```

🔗 Default file path for **Epic Games** users:

```text
C:\Program Files\Epic Games\rocketleague\TAGame\Config\DefaultStatsAPI.ini
```

✏️ Then edit this file as follows and save it:

```ini
Port=49123
PacketSendRate=120
```

`PacketSendRate=60` also works, but `120` is recommended for a better experience.

#### 3️⃣ - Restart the Game:

After completing all steps, restart your game.

#### ⚠️ - Status Checks:

You can check the following statuses to make sure the program is working correctly:

🟢 `CONNECTED`: If you see this text in the **API Connection** section of the program, the process is complete.

🟠 `WAITING...`: If you see this text in the **API Connection** section of the program, make sure you configured the file correctly and restarted the game. If neither helps, try closing and reopening the program.

---

### 📌 General Recommendations

To experience the Alpha Boost sound in a better way, it is recommended that you follow these suggestions:

- Use the recommended profile, `Quality`.
- Set the `PacketSendRate` value in the API file to `120`.
- Check that the program volume is not low or muted in the **Windows Volume Mixer**.
- Lower your in-game sound level so it does not overpower the **Alpha Boost** sound (recommended). Alternatively, increase the **Volume** value in the program.
- Find the best audio levels according to your own sound setup and use them that way. For a better experience, it is recommended not to keep the **Volume** value too high.

For the `Quality` profile, it is recommended to keep the **Volume** value at 50% or below.

For the `Advanced` profile, it is recommended to keep the **Volume** value at 30% or below.

### 📄 License

This project is released under the MIT License.

---

<a id="turkce"></a>
## 🇹🇷 Türkçe

## 🎬 Ön İzleme

Devam etmeden önce aşağıdaki videoyu ve ekran görüntüsünü inceleyerek program hakkında hızlı bir şekilde bilgi sahibi olabilirsiniz:

<p align="center">
  <video src="https://github.com/user-attachments/assets/8dcaedb0-ec1b-4ab3-bb69-4ab9269747d1" width="100%" controls>
    Your browser does not support the video tag.
  </video>
</p>
<img width="413" height="410" alt="image" src="https://github.com/user-attachments/assets/6c3c7bea-6a5d-45b7-82fa-0ed67bcd0b78" />


### ✨ Genel Bakış

**Alpha Boost Engine**, oyun dosyalarını değiştirmeden ve farklı mod yöntemlerine ihtiyaç duymadan Alpha Boost ses deneyimi yaşamak isteyen oyuncular için hazırlanmış bir masaüstü uygulamasıdır.

Bu program gerçek Alpha Boost ögesini oyuna eklemez veya zorla açmaz. Bunun yerine harici ses dosyalarından oluşmuş sesleri kullanarak oyundaki araba hızınıza bağlı olacak şekilde değiştirerek Alpha Boost sesini oluşturur.

---

### 🛡️ Güvenlik

Bu program, oyuncuların en çok çekindiği alanlardan uzak duracak şekilde tasarlanmıştır.

- Rocket League dosyalarını değiştirmez.
- Rocket League dosyalarına herhangi bir ek müdahalede bulunmaz.
- Rocket League dosyalarını okumaz.

⚪️ Harici bir ses uygulaması olarak çalışır. Kısacası, **Easy Anti-Cheat** sisteminden çekinen oyuncular için ideal bir çözümdür.

---

### ❔ Nasıl Çalışır?

Ses motoru temelde şu üç durumu bir araya getirir (API):

- Boost basılıp basılmadığının anlık olarak takibi,
- Boost miktarının harcanma durumunun kontrolü,
- Araba hızının anlık olarak kontrolü,

⚪️ Bu veriler harmanlanarak Alpha Boost sesinin ne zaman ve hangi tonda (hıza duyarlı olarak) çalacağı belirlenir. Bu akıllı yapı sayesinde, gol tekrarlarında veya boost miktarınız **0** iken tuşa bastığınızda sesin gereksiz yere tetiklenmesi önlenir.
  
---

### 👥 Profiller

Her profili test edip size en uygun olanı seçebilirsiniz.

| Profil | Açıklama | Kısa Bilgi |
| --- | --- | --- |
| `Quality` | Hıza göre en detaylı tepki veren ve geçişleri daha yumuşak olan profil | En İyi Seçim |
| `Advanced` | Hıza göre tepki veren fakat ses düzeyi daha yüksek olan profil | Daha Gür Ses |
| `Normal` | Tüm hızlarda aynı sesi veren sabit profil | En Sade Kullanım |

---

### ❇️ Kurulum Aşamaları

#### 1️⃣ - Programı İndir:

- En güncel sürümü [buradan indirin](https://github.com/trznx/Rocket_League-Alpha_Boost/releases) ve `.exe` dosyasını masaüstünüze veya başka bir klasörün içerisine atın.

- Ardından `.exe` dosyasını çalıştırın.

#### 2️⃣ - API Yapılandırması:

🔗 **Steam** kullanıcıları için varsayılan dosya yolu:

```text
C:\Program Files (x86)\Steam\steamapps\common\rocketleague\TAGame\Config\DefaultStatsAPI.ini
```

🔗 **Epic Games** kullanıcıları için varsayılan dosya yolu:

```text
C:\Program Files\Epic Games\rocketleague\TAGame\Config\DefaultStatsAPI.ini
```

✏️ Ardından bu dosyayı şu şekilde düzenleyin ve kaydedin:

```ini
Port=49123
PacketSendRate=120
```

`PacketSendRate=60` değeri için de çalışır ancak daha iyi bir deneyim için `120` önerilir.

#### 3️⃣ - Oyunu Yeniden Başlat:

Tüm işlemleri bitirdikten sonra oyununuzu yeniden başlatın.

#### ⚠️ - Durum Kontrolleri:

Programın doğru bir şekilde çalışıp çalışmadığından emin olmak için şu durumları kontrol edebilirsiniz:

🟢 `CONNECTED`: Programdaki **API Connection** kısmında bu yazı yazıyorsa süreç tamamlanmıştır.

🟠 `WAITING...`: Programdaki **API Connection** kısmında bu yazı yazıyorsa dosyayı doğru yapılandırdığınızdan ve oyunu yeniden başlattığınızdan emin olun. Her iki durum da işe yaramazsa programı kapatıp yeniden açmayı deneyin.

---

### 📌 Genel Tavsiyeler

Alpha Boost sesini daha iyi deneyimlemek için bu tavsiyelere uymanız önerilir:

- Önerilen profil olan `Quality` profilini kullanın.
- API dosyasındaki `PacketSendRate` değerini `120` olarak ayarlayın.
- Programın ses düzeyinin **Windows Ses Karıştırıcısı** bölümünde kısık veya sessizde olmadığını kontrol edin.
- Oyun içi ses düzeyinizi, **Alpha Boost** sesini bastırmaması için düşürün (önerilen). Alternatif olarak programdaki **Volume** değerini artırın.
- Kendi ses seviyelerinize göre en iyi ses düzeylerini bulun ve ona göre kullanın. Daha iyi bir deneyim için **Volume** değerini yüksek tutmamanız önerilir.

`Quality` profili için **Volume** değerini %50 ve daha altında tutmanız önerilir.

`Advanced` profili için **Volume** değerini %30 ve daha altında tutmanız önerilir.

### 📄 Lisans

Bu proje MIT Lisansı ile sunulmaktadır.
