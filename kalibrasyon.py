import cv2
import mss
import numpy as np
import time
import json
import os

print("="*50)
print("  ALPHA BOOST - KALİBRASYON ARACI")
print("="*50)
print("1. Oyuna girin ve Serbest Antrenman (Freeplay) açın.")
print("2. Boost'unuzu tamamen bitirin (Ekranda 0 yazsın).")
print("3. Bu yazıdan sonra 5 saniyeniz var, oyuna dönüp bekleyin...")

for i in range(5, 0, -1):
    print(f"{i} saniye...")
    time.sleep(1)

print("Ekran görüntüsü alınıyor...")

with mss.mss() as sct:
    # Tüm ekranı al
    monitor = sct.monitors[1]
    img_bgra = np.array(sct.grab(monitor))

# BGR formatına çevir
img = cv2.cvtColor(img_bgra, cv2.COLOR_BGRA2BGR)
cv2.imwrite("debug_tam_ekran.png", img) # Debug için kaydet

print("\nGörüntü alındı! Şimdi ekrana bir pencere gelecek.")
print("Lütfen fare ile sadece '0' rakamının etrafını çizin.")
print("Çizdikten sonra kaydetmek için ENTER veya SPACE tuşuna basın.")
print("Eğer yanlış çizerseniz, tekrar çizmek için farenizle yeni bir kutu çizebilirsiniz.")

cv2.namedWindow("Lutfen 0 rakamini secip ENTER'a basin", cv2.WINDOW_NORMAL)
r = cv2.selectROI("Lutfen 0 rakamini secip ENTER'a basin", img, showCrosshair=True, fromCenter=False)
cv2.destroyAllWindows()

if r[2] == 0 or r[3] == 0:
    print("Seçim iptal edildi.")
    exit()

x, y, w, h = int(r[0]), int(r[1]), int(r[2]), int(r[3])
print(f"\nSeçilen Bölge: X:{x}, Y:{y}, Genişlik:{w}, Yükseklik:{h}")

# Sadece seçilen kısmı kes
cropped = img[y:y+h, x:x+w]
cv2.imwrite("debug_kesilmis_bolge.png", cropped) # Debug için kaydet

# Dinamik Eşik Değeri Hesaplama (Kullanıcının ekran parlaklığına göre)
gray = cv2.cvtColor(cropped, cv2.COLOR_BGR2GRAY)
max_val = np.max(gray)
mean_val = np.mean(gray)

# Parlaklık çok düşükse hata verelim
if max_val < 30:
    print("HATA: Seçilen bölge kapkaranlık! Boost UI bulunamadı.")
    exit()

# Eşiği arka plan ile yazının arasında tam en ideal noktaya koyuyoruz
dynamic_thresh = int(mean_val + (max_val - mean_val) * 0.7)

print(f"Hesaplanan Dinamik Eşik Değeri: {dynamic_thresh} (Max: {max_val}, Ortalama: {int(mean_val)})")

_, thresh = cv2.threshold(gray, dynamic_thresh, 255, cv2.THRESH_BINARY)

cv2.imwrite("template_0.png", thresh)
print("Şablon (template_0.png) başarıyla kaydedildi!")

config = {"left": x, "top": y, "width": w, "height": h, "threshold": dynamic_thresh}
with open("config.json", "w") as f:
    json.dump(config, f)

print("Koordinatlar (config.json) başarıyla kaydedildi!")
print("ÖNEMLİ: Masaüstünde oluşan 'template_0.png' dosyasını açıp bakın.")
print("İçinde sadece beyaz bir '0' ve siyah arka plan görmelisiniz.")
print("Eğer tamamen siyahsa kalibrasyon hatalı olmuştur.")
print("="*50)
