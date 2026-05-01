# Rocket League Alpha Boost Engine

Bu proje, oyunun orijinal dosyalarını değiştirmeden (Anti-Cheat güvenli) profesyonel Alpha Boost seslerini dinamik fizik hesaplamalarıyla simüle eden akıllı bir ses motorudur.

## Özellikler
- **Gerçekçi Fizik Motoru**: Sadece tuşa basma süreniz değil, 8 kademeli ara hız .wav dosyaları sayesinde hızınıza göre kusursuz geçişler sağlanır.
- **Güvenli (Anti-Cheat Uyumlu)**: Oyunun RAM'ini (hafızasını) okumaz. Tamamen pikselleri analiz ederek çalışır.
- **Kullanıcı Dostu Arayüz (GUI)**: Kurulumu tamamladıktan sonra ayarlara Python kodu içinden değil, basit bir arayüz ekranından ulaşabilirsiniz.
- **Özelleştirilebilir Kalibrasyon**: Sadece sizin monitörünüze ve oyun içi arayüz (UI) büyüklüğünüze göre kişiselleştirilir.

## Gereksinimler
Herhangi bir modern Windows bilgisayarda çalışır. Oyunda **FPS düşüşüne sebep olmaz**, en hızlı ekran okuma kütüphanesi olan `mss` kullanılmıştır.

## Kurulum ve Başlatma

1. Python yüklü olduğundan emin olun.
2. Bu klasörü bilgisayarınıza indirin.
3. Terminal (Komut İstemi) açın ve gerekli kütüphaneleri kurun:
   ```cmd
   pip install -r requirements.txt
   ```
4. **Kalibrasyon Aşaması (Sadece 1 Kere Yapılacak):**
   - Oyuna girin, antrenman (Freeplay) modunu açın.
   - Boostunuz "0" (Sıfır) olana kadar harcayın.
   - Oyunu "Pencereli Tam Ekran" (Borderless) moduna alın.
   - Terminalden `python kalibrasyon.py` komutunu çalıştırın. Kendi kendine ekranınızın 0 rakamını bulup ayar dosyanızı kaydedecektir.
5. **Programı Başlatma:**
   - Kalibrasyon bittikten sonra, oynamaya başlamadan önce `python main.py` yazın.
   - Karşınıza çıkan **Arayüz (GUI)** üzerinden ses seviyesini ayarlayabilir, motoru kapatıp açabilir ve Sınırsız Boost (Freeplay) modunu değiştirebilirsiniz.

> **Not:** Program çalıştığı sürece klavye/mouse girdilerinizi ve ekranın sadece boost sayacının olduğu kısmını okur.

İyi oyunlar!
