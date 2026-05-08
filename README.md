# Rocket League Alpha Boost Engine

[English](#english) | [Türkçe](#turkce)

Rocket League Alpha Boost Engine is a Windows desktop app that recreates the Alpha Boost feel with external audio playback driven by Rocket League's local Stats API and local boost input.

The current version does not use screen reading or calibration.

---

<a id="english"></a>
## English

### Overview

This project is built for players who want an Alpha Boost style audio experience without modifying Rocket League files or injecting into the game process.

The app combines:

- Rocket League's local Stats API
- Local boost button detection
- Speed-based sound profile playback

This makes playback far more reliable than a simple key listener and helps prevent false triggers during countdown, no-boost states, and other edge cases.

### Current Features

- Official local Stats API support over `127.0.0.1:49123`
- Reliable boost detection using both input state and real API-confirmed boost activity
- Multiplayer-safe player tracking
- Three selectable sound profiles:
  - `Advanced`
  - `Quality`
  - `Normal`
- Live API connection indicator in the interface
- Volume control and quick engine toggle support
- No memory scanning, no DLL injection, no pixel calibration

### How It Works

The engine decides when to play sound by combining:

- Local boost input
- API-confirmed boost usage
- Current vehicle speed from the API

This prevents common problems such as:

- False playback while pressing boost during kickoff countdown
- Playback when boost cannot actually be consumed
- Missing or unstable speed-reactive transitions in normal gameplay

### Profiles

| Profile | Behavior | Source Folder |
| --- | --- | --- |
| `Advanced` | Speed-reactive playback with 4 sound bands | `assets/sounds/alpha_boost_advanced` |
| `Quality` | Speed-reactive playback with 6 sound bands | `assets/sounds/alpha_boost_quality` |
| `Normal` | Constant playback at all speeds | `assets/sounds/alpha_boost_normal` |

#### Advanced Profile Mapping

| Speed | File |
| --- | --- |
| `0-500 uu/s` | `0_gr.wav` |
| `501-1000 uu/s` | `750_gr.wav` |
| `1001-1500 uu/s` | `1400_gr.wav` |
| `1501+ uu/s` | `1700_gr.wav` |

#### Quality Profile Mapping

| Speed | File |
| --- | --- |
| `0-300 uu/s` | `gr_level_150.wav` |
| `301-600 uu/s` | `gr_level_450.wav` |
| `601-900 uu/s` | `gr_level_750.wav` |
| `901-1200 uu/s` | `gr_level_1050.wav` |
| `1201-1500 uu/s` | `gr_level_1350.wav` |
| `1501+ uu/s` | `gr_level_1650.wav` |

### Safety Notes

This tool is designed as an external companion application.

- It does not patch Rocket League files.
- It does not inject into the Rocket League process.
- It does not scan Rocket League memory.
- It depends on Rocket League's own local Stats API plus local input state.

Each user must enable the Stats API locally on their own game installation.

### Enable the Rocket League Stats API

Before using the app, enable the API in your local `DefaultStatsAPI.ini`.

Minimum required values:

```ini
Port=49123
PacketSendRate=120
```

`PacketSendRate=60` also works, but `120` is recommended for smoother updates.

If the interface shows `WAITING...`, check your local API configuration first.

### Installation

#### Option 1: Run the packaged app

1. Download the latest release build.
2. Keep the executable and bundled asset folders in the same directory.
3. Launch the app.
4. Start Rocket League.
5. Confirm that the interface shows `API Connection -> CONNECTED`.

#### Option 2: Run from source

1. Install Python 3.11 or newer.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Start the app:

```bash
python main.py
```

### Build

To generate a standalone executable:

```bash
pyinstaller AlphaBoostEngine.spec
```

### Recommended Setup

- Use any in-game boost visual you want.
- Lower the in-game boost sound if you want the external Alpha Boost layer to stand out more clearly.
- Start with `Advanced` or `Quality` if you want speed-based playback.
- Use `Normal` if you want a simple constant profile.

### Limitations

- This is external audio playback, so it will never behave exactly like a native in-game item.
- Short differences can happen during packet loss, alt-tab transitions, API interruptions, or abrupt gameplay changes.
- The app depends on your local Stats API configuration being active and stable.

### Media Placeholders

Replace the placeholders below with your own links.

#### Screenshots

- Main interface: `[LINK]`
- Profile selection: `[LINK]`
- In-game example: `[LINK]`

#### Videos

- Main showcase: `[LINK]`
- Advanced profile demo: `[LINK]`
- Quality profile demo: `[LINK]`

### Project Structure

```text
RL_AlphaBoost/
|-- assets/
|-- icon/
|-- interface_icons/
|-- api_client.py
|-- audio_engine.py
|-- interface.py
|-- main.py
|-- requirements.txt
|-- AlphaBoostEngine.spec
`-- README.md
```

Only actively used runtime files are kept in the project root. Old tools, experiments, and helper scripts are kept outside the main runtime path.

### Privacy and Repository Notes

- Personal configuration files such as `user_settings.json` are not tracked.
- Local caches, logs, builds, and experimental files are ignored through `.gitignore`.
- The repository does not include personal API credentials, account-bound secrets, or user-specific local settings.

### License

This project is released under the MIT License.

---

<a id="turkce"></a>
## Türkçe

### Genel Bakış

Bu proje, Rocket League dosyalarına veya oyun sürecine müdahale etmeden Alpha Boost benzeri bir ses deneyimi sunmak için geliştirilmiş harici bir Windows masaüstü uygulamasıdır.

Uygulama şu yapıyı bir araya getirir:

- Rocket League'in yerel Stats API'si
- Yerel boost tuş girdisi takibi
- Hıza göre değişen ses profilleri

Bu sayede sadece tuşa basıldığını dinleyen basit sistemlere göre çok daha kararlı çalışır ve geri sayım anı, boost harcanamayan durumlar veya benzer kenar senaryolarda yanlış ses tetiklemelerini büyük ölçüde engeller.

### Güncel Özellikler

- `127.0.0.1:49123` üzerinden resmi yerel Stats API desteği
- Yerel giriş durumu ile gerçek API boost bilgisini birleştiren daha güvenilir boost algılama
- Çok oyunculu maçlarda daha kararlı oyuncu takibi
- Üç farklı ses profili:
  - `Advanced`
  - `Quality`
  - `Normal`
- Arayüz üzerinde canlı API bağlantı durumu
- Ses seviyesi kontrolü ve hızlı motor açma/kapatma desteği
- Hafıza taraması yok, DLL inject yok, piksel kalibrasyonu yok

### Nasıl Çalışır?

Sesin ne zaman çalacağı şu veriler birleştirilerek belirlenir:

- Yerel boost tuş girdisi
- API tarafından doğrulanan gerçek boost kullanımı
- API'den gelen anlık araç hızı

Bu yaklaşım özellikle şu sorunları azaltmak için kullanılır:

- Kickoff geri sayımında boost'a basınca yanlış ses çalması
- Boost gerçekten harcanmıyorken ses tetiklenmesi
- Hıza bağlı geçişlerin bazı anlarda kararsız davranması

### Profiller

| Profil | Davranış | Kaynak Klasör |
| --- | --- | --- |
| `Advanced` | 4 ses bandı ile hıza duyarlı oynatma, yüksek ses | `assets/sounds/alpha_boost_advanced` |
| `Quality` | 6 ses bandı ile daha detaylı hıza duyarlı oynatma | `assets/sounds/alpha_boost_quality` |
| `Normal` | Tüm hızlarda sabit ses | `assets/sounds/alpha_boost_normal` |

#### Advanced Profil Eşlemesi

| Hız | Dosya |
| --- | --- |
| `0-500 uu/s` | `0_gr.wav` |
| `501-1000 uu/s` | `750_gr.wav` |
| `1001-1500 uu/s` | `1400_gr.wav` |
| `1501+ uu/s` | `1700_gr.wav` |

#### Quality Profil Eşlemesi

| Hız | Dosya |
| --- | --- |
| `0-300 uu/s` | `gr_level_150.wav` |
| `301-600 uu/s` | `gr_level_450.wav` |
| `601-900 uu/s` | `gr_level_750.wav` |
| `901-1200 uu/s` | `gr_level_1050.wav` |
| `1201-1500 uu/s` | `gr_level_1350.wav` |
| `1501+ uu/s` | `gr_level_1650.wav` |

### Güvenlik Notları

Bu araç harici bir yardımcı uygulama olarak tasarlanmıştır.

- Rocket League dosyalarını değiştirmez.
- Rocket League sürecine inject etmez.
- Rocket League hafızasını taramaz.
- Rocket League'in kendi yerel Stats API'si ile yerel giriş durumuna dayanır.

API'yi her kullanıcının kendi bilgisayarında ayrıca etkinleştirmesi gerekir.

### Rocket League Stats API Nasıl Açılır?

Uygulamayı kullanmadan önce kendi yerel `DefaultStatsAPI.ini` dosyanızda Stats API'yi etkinleştirin.

Gerekli minimum değerler:

```ini
Port=49123
PacketSendRate=120
```

`PacketSendRate=60` da çalışır, ancak daha akıcı güncellemeler için `120` önerilir.

Arayüzde `WAITING...` görüyorsanız önce yerel API ayarlarınızı kontrol edin.

### Kurulum

#### Seçenek 1: Paketlenmiş uygulamayı çalıştırma

1. En güncel release yapısını indirin.
2. `.exe` dosyasını ve gerekli asset klasörlerini aynı dizinde tutun.
3. Uygulamayı başlatın.
4. Rocket League'i açın.
5. Arayüzde `API Connection -> CONNECTED` yazdığını doğrulayın.

#### Seçenek 2: Kaynak koddan çalıştırma

1. Python 3.11 veya daha yeni bir sürüm kurun.
2. Bağımlılıkları yükleyin:

```bash
pip install -r requirements.txt
```

3. Uygulamayı başlatın:

```bash
python main.py
```

### Build Alma

Tek dosyalık `.exe` üretmek için:

```bash
pyinstaller AlphaBoostEngine.spec
```

### Önerilen Kullanım

- İstediğiniz boost görselini kullanabilirsiniz.
- Harici Alpha Boost sesinin daha net duyulması için oyun içi boost sesini kısabilirsiniz.
- Hıza göre değişen oynatma istiyorsanız önce `Advanced` veya `Quality` profillerini deneyin.
- Sabit ve daha sade bir kullanım istiyorsanız `Normal` profilini tercih edin.

### Sınırlamalar

- Bu sistem harici ses oynatma kullandığı için oyun içi orijinal bir item gibi birebir davranmaz.
- Paket kaybı, alt-tab geçişleri, API kesintileri veya ani oyun içi değişimler kısa süreli farklar oluşturabilir.
- Uygulama, yerel Stats API yapılandırmanızın aktif ve kararlı olmasına bağlıdır.

### Medya Yer Tutucuları

Aşağıdaki `[LINK]` alanlarını kendi bağlantılarınızla değiştirebilirsiniz.

#### Ekran Görüntüleri

- Ana arayüz: `[LINK]`
- Profil seçimi: `[LINK]`
- Oyun içi örnek: `[LINK]`

#### Videolar

- Genel tanıtım: `[LINK]`
- Advanced profil demosu: `[LINK]`
- Quality profil demosu: `[LINK]`

### Proje Yapısı

```text
RL_AlphaBoost/
|-- assets/
|-- icon/
|-- interface_icons/
|-- api_client.py
|-- audio_engine.py
|-- interface.py
|-- main.py
|-- requirements.txt
|-- AlphaBoostEngine.spec
`-- README.md
```

Aktif olarak kullanılan çalışma dosyaları root dizinde tutulur. Eski araç script'leri, deneysel dosyalar ve yardımcı içerikler ana çalışma yolunun dışında bırakılmıştır.

### Gizlilik ve Repo Notları

- `user_settings.json` gibi kişisel yapılandırma dosyaları takip edilmez.
- Yerel cache, log, build ve deneysel dosyalar `.gitignore` ile dışarıda bırakılır.
- Repo içerisinde kişisel API anahtarı, hesap verisi veya kullanıcıya özel gizli bilgi bulunmaz.

### Lisans

Bu proje MIT Lisansı ile sunulmaktadır.
