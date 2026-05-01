# Rocket League Alpha Boost Engine

Bu proje, oyunun orijinal dosyalarını değiştirmeden (Anti-Cheat güvenli) profesyonel Alpha Boost seslerini dinamik fizik hesaplamalarıyla simüle eden akıllı bir ses motorudur.

## Özellikler
- **Gerçekçi Fizik Motoru**: Sadece tuşa basma süreniz değil, 8 kademeli ara hız .wav dosyaları sayesinde hızınıza göre kusursuz geçişler sağlanır.
- **Güvenli (Anti-Cheat Uyumlu)**: Oyunun RAM'ini (hafızasını) okumaz. Tamamen pikselleri analiz ederek çalışır.
- **Kullanıcı Dostu Arayüz (GUI)**: Kurulumu tamamladıktan sonra ayarlara Python kodu içinden değil, basit bir arayüz ekranından ulaşabilirsiniz.
- **Özelleştirilebilir Kalibrasyon**: Sadece sizin monitörünüze ve oyun içi arayüz (UI) büyüklüğünüze göre kişiselleştirilir.

## Sistem Gereksinimleri ve Performans
Bu program, bilgisayarınızı **kesinlikle yormayacak şekilde** özel olarak optimize edilmiştir.
- **FPS Düşüşü Yaşanmaz:** Oyun içi FPS'inizi etkilemez. Ekran okuma kütüphanesi olarak piyasadaki en hızlı araç olan `mss` kullanılmıştır.
- **Mikro-Alan Taraması (Micro-Region Capture):** Program saniyede 60 kez tüm ekranınızı okumaz! Kalibrasyon aşamasında belirlediğiniz o minicik "0" bölgesini (yaklaşık 70x70 piksel) okur. Bu sayede ekranınızın %99.9'u işlemci tarafından görmezden gelinir ve CPU kullanımı **%1'in altında** kalır.
- **Sıfır Gecikme (Ultra-Low Latency):** Ses motoru C tabanlı PyGame kullanılarak `buffer=256` değerine ayarlanmıştır. Bu sayede Boost'a bastığınız an ile sesi duyduğunuz an arasındaki gecikme sadece ~15 milisaniyedir (insan kulağının algılayamayacağı kadar düşük).

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
