"""
Alpha Boost Engine - WebSocket API Client
==========================================
Rocket League'in yerel WebSocket API'sine (ws://localhost:49123) baglanir.
Saniyede 120 paket hizinda gelen JSON verilerinden:
  - Speed (v): Arabanin anlik hizi (uu/s)
  - bBoosting: Boost tusuna basilip basilmadigi (True/False)
bilgilerini okur ve thread-safe bir sekilde paylasir.

Baglanti koparsa sessizce yeniden dener, hata vermez.
"""

import threading
import json
import time

try:
    import websocket
except ImportError:
    print("  [API] HATA: 'websocket-client' kutuphanesi bulunamadi!")
    print("  [API] Kurulum: pip install websocket-client")
    websocket = None


class RocketLeagueAPI:
    """Rocket League WebSocket API istemcisi.
    
    Kullanim:
        api = RocketLeagueAPI()
        api.start()  # Arka plan thread'i baslatir
        
        # Ana dongu icinde:
        speed = api.speed           # Anlik hiz (float, uu/s)
        boosting = api.is_boosting  # Boost basili mi (bool)
        connected = api.connected   # API'ye bagli mi (bool)
    """
    
    WS_URL = "ws://localhost:49123"
    RECONNECT_DELAY = 2.0  # Baglanti koparsa kac saniye bekleyip tekrar denesin
    
    def __init__(self):
        # Thread-safe paylasilacak veriler
        self._lock = threading.Lock()
        self._speed = 0.0
        self._is_boosting = False
        self._connected = False
        
        # Arka plan thread'i
        self._thread = None
        self._running = False
    
    # ─── PUBLIC PROPERTIES (Thread-Safe) ─────────────────────────────────────
    
    @property
    def speed(self) -> float:
        """Arabanin anlik hizi (uu/s). API baglantisindan okunur."""
        with self._lock:
            return self._speed
    
    @property
    def is_boosting(self) -> bool:
        """Boost tusu basili mi?"""
        with self._lock:
            return self._is_boosting
    
    @property
    def connected(self) -> bool:
        """WebSocket API'sine bagli mi?"""
        with self._lock:
            return self._connected
    
    # ─── LIFECYCLE ───────────────────────────────────────────────────────────
    
    def start(self):
        """Arka plan thread'ini baslatir. Birden fazla kez cagirilabilir (guvenli)."""
        if self._thread is not None and self._thread.is_alive():
            return
        self._running = True
        self._thread = threading.Thread(target=self._connection_loop, daemon=True)
        self._thread.start()
    
    def stop(self):
        """Arka plan thread'ini durdurur."""
        self._running = False
        with self._lock:
            self._speed = 0.0
            self._is_boosting = False
            self._connected = False
    
    # ─── INTERNAL ────────────────────────────────────────────────────────────
    
    def _connection_loop(self):
        """Surekli baglanti deneyen ana dongu. Kopmada otomatik yeniden baglanir."""
        while self._running:
            try:
                ws = websocket.WebSocket()
                ws.settimeout(5.0)
                ws.connect(self.WS_URL)
                
                with self._lock:
                    self._connected = True
                print(f"  [API] Rocket League'e basariyla baglandi! ({self.WS_URL})")
                
                # Veri okuma dongusu
                while self._running:
                    try:
                        raw = ws.recv()
                        if not raw:
                            break
                        self._parse_packet(raw)
                    except websocket.WebSocketTimeoutException:
                        # Timeout oldu ama baglanti hala acik olabilir
                        continue
                    except (websocket.WebSocketConnectionClosedException, ConnectionError):
                        break
                        
            except Exception as e:
                # Baglanti kurulamadi veya koptu
                pass
            finally:
                with self._lock:
                    self._connected = False
                    self._speed = 0.0
                    self._is_boosting = False
                
                try:
                    ws.close()
                except Exception:
                    pass
            
            # Yeniden baglanmadan once bekle
            if self._running:
                time.sleep(self.RECONNECT_DELAY)
    
    def _parse_packet(self, raw: str):
        """Gelen JSON paketini cozumler ve verileri gunceller.
        
        Beklenen format ornegi:
        {"Speed": 1542.3, "bBoosting": true, ...}
        
        Not: API'nin gonderdigi tam JSON yapisina gore
        alan isimleri burada ayarlanmalidir.
        """
        try:
            data = json.loads(raw)
            
            # API'den gelen alan adlari (bunlar API'nin gercek yapisina gore degisebilir)
            speed = float(data.get("Speed", data.get("speed", data.get("v", 0.0))))
            boosting = bool(data.get("bBoosting", data.get("boosting", data.get("isBoosting", False))))
            
            with self._lock:
                self._speed = speed
                self._is_boosting = boosting
                
        except (json.JSONDecodeError, ValueError, TypeError):
            # Bozuk paket, atla
            pass
