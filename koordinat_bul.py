import mss
import cv2
import numpy as np

# Ekran çözünürlüğüne göre bu rakamları değiştirerek boost dairesini tam içine alacak şekilde ayarla.
# (Şu anki değerler tahmini 1080p bir ekran içindir)
BOOST_REGION = {"top": 850, "left": 1700, "width": 180, "height": 180}

print("Koordinat test ekranı açılıyor... Kapatmak için o penceredeyken 'q' tuşuna bas.")

with mss.mss() as sct:
    while True:
        # Belirlenen bölgenin anlık görüntüsünü al
        img = np.array(sct.grab(BOOST_REGION))
        
        # Görüntüyü ekrana yansıt
        cv2.imshow("Boost Gostergesi", img)
        
        # Ortalama parlaklığı konsola yazdır (0 olduğunda ve doluyken bu rakamları gözlemle)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        print(f"Anlik Parlaklik: {np.mean(gray):.2f}", end="\r")
        
        if cv2.waitKey(25) & 0xFF == ord('q'):
            break

cv2.destroyAllWindows()