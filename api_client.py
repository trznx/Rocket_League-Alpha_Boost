"""
Alpha Boost Engine - TCP API Client
=====================================
Rocket League'in RESMI Stats API'sine (TCP localhost:49123) baglanir.
Bu bir WebSocket DEGIL, ham TCP soketidir!

Oyun sunucu gorevindedir ve port 49123 uzerinden JSON verisi yayinlar.
Bizim programimiz client olarak bu porta baglanir.

Aktivasyon:
  TAGame/Config/DefaultStatsAPI.ini -> PacketSendRate=120, Port=49123
"""

import threading
import json
import time
import socket


class RocketLeagueAPI:
    """Rocket League resmi Stats API istemcisi (TCP).
    
    Kullanim:
        api = RocketLeagueAPI()
        api.start()
        
        speed = api.speed           # Anlik hiz (float, uu/s)
        boosting = api.is_boosting  # Boost basili mi (bool)
        connected = api.connected   # API'ye bagli mi (bool)
    """
    
    HOST = "127.0.0.1"
    PORT = 49123
    RECONNECT_DELAY = 2.0
    BUFFER_SIZE = 4096
    
    def __init__(self):
        self._lock = threading.Lock()
        self._speed = 0.0        # uu/s cinsinden (donusturulmus)
        self._speed_raw = 0.0    # API'den gelen ham deger (km/h)
        self._is_boosting = False
        self._boost_amount = 100  # 0-100 arasi boost miktari
        self._last_boost_activity_time = 0.0
        self._prev_boost_amount = None
        self._connected = False
        self._last_error = ""
        self._packet_count = 0
        
        self._thread = None
        self._running = False
    
    # API hizi km/h cinsinden geliyor, biz uu/s kullaniyoruz
    # Supersonic (~2200 uu/s) = ~82 km/h  =>  1 km/h = ~27.71 uu/s
    SPEED_CONVERSION = 2300.0 / 83.0  # ~27.71
    BOOST_ACTIVITY_WINDOW = 0.06
    
    # ─── PUBLIC PROPERTIES ───────────────────────────────────────────────────
    
    @property
    def speed(self) -> float:
        with self._lock:
            return self._speed
    
    @property
    def is_boosting(self) -> bool:
        with self._lock:
            return self._is_boosting
    
    @property
    def connected(self) -> bool:
        with self._lock:
            return self._connected
    
    @property
    def last_error(self) -> str:
        with self._lock:
            return self._last_error
    
    @property
    def boost_amount(self) -> int:
        """Boost miktari (0-100). API'de yoksa 100 doner."""
        with self._lock:
            return self._boost_amount
    
    # ─── LIFECYCLE ───────────────────────────────────────────────────────────
    
    def start(self):
        if self._thread is not None and self._thread.is_alive():
            return
        self._running = True
        self._thread = threading.Thread(target=self._connection_loop, daemon=True)
        self._thread.start()
    
    def stop(self):
        self._running = False
        with self._lock:
            self._speed = 0.0
            self._is_boosting = False
            self._boost_amount = 100
            self._last_boost_activity_time = 0.0
            self._prev_boost_amount = None
            self._connected = False
    
    # ─── INTERNAL ────────────────────────────────────────────────────────────
    
    def _connection_loop(self):
        """Ham TCP baglantisi ile oyundan veri okur."""
        retry_count = 0
        
        while self._running:
            sock = None
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(5.0)
                sock.connect((self.HOST, self.PORT))
                
                with self._lock:
                    self._connected = True
                    self._last_error = ""
                    self._packet_count = 0
                retry_count = 0
                print(f"  [API] Rocket League'e baglandi! (TCP {self.HOST}:{self.PORT})", flush=True)
                
                # Veri tamponu - TCP parcali veri gonderebilir
                buffer = ""
                raw_debug_shown = False
                
                while self._running:
                    try:
                        data = sock.recv(self.BUFFER_SIZE)
                        if not data:
                            print("  [API] Baglanti kapandi (bos veri)", flush=True)
                            break
                        
                        decoded = data.decode("utf-8", errors="replace")
                        
                        # DEBUG: Ilk gelen ham veriyi goster
                        if not raw_debug_shown:
                            preview = decoded[:500].replace('\n', '\\n').replace('\r', '\\r')
                            print(f"  [API] HAM VERI (ilk {len(decoded)} byte): {preview}", flush=True)
                            raw_debug_shown = True
                        
                        buffer += decoded
                        
                        # JSON nesnelerini ayikla
                        # TCP akisinda birden fazla JSON nesnesi art arda gelebilir
                        while buffer:
                            buffer = buffer.lstrip()
                            if not buffer:
                                break
                            
                            # Ilk JSON nesnesini bul
                            if buffer[0] == '{':
                                depth = 0
                                end_idx = -1
                                in_string = False
                                escape = False
                                
                                for idx, ch in enumerate(buffer):
                                    if escape:
                                        escape = False
                                        continue
                                    if ch == '\\':
                                        escape = True
                                        continue
                                    if ch == '"':
                                        in_string = not in_string
                                        continue
                                    if in_string:
                                        continue
                                    if ch == '{':
                                        depth += 1
                                    elif ch == '}':
                                        depth -= 1
                                        if depth == 0:
                                            end_idx = idx
                                            break
                                
                                if end_idx >= 0:
                                    json_str = buffer[:end_idx + 1]
                                    buffer = buffer[end_idx + 1:]
                                    self._parse_packet(json_str)
                                else:
                                    # Henuz tam JSON gelmedi, daha fazla veri bekle
                                    break
                            else:
                                # JSON olmayan karakter, atla
                                buffer = buffer[1:]
                                
                    except socket.timeout:
                        # Timeout oldu ama baglanti hala acik
                        continue
                    except (ConnectionError, OSError):
                        print("  [API] Baglanti koptu", flush=True)
                        break
                        
            except ConnectionRefusedError:
                if retry_count == 0:
                    print(f"  [API] Baglanti reddedildi - Oyun acik mi? DefaultStatsAPI.ini ayarli mi?", flush=True)
                    print(f"  [API] Kontrol: PacketSendRate=120, Port=49123 olmali", flush=True)
                with self._lock:
                    self._last_error = "Connection refused"
                    
            except socket.timeout:
                if retry_count == 0:
                    print(f"  [API] Baglanti zaman asimina ugradi", flush=True)
                with self._lock:
                    self._last_error = "Timeout"
                    
            except OSError as e:
                if retry_count == 0:
                    print(f"  [API] OS Hatasi: {e}", flush=True)
                with self._lock:
                    self._last_error = f"OS: {e}"
                    
            except Exception as e:
                if retry_count == 0:
                    print(f"  [API] Beklenmeyen hata: {type(e).__name__}: {e}", flush=True)
                with self._lock:
                    self._last_error = f"{type(e).__name__}: {e}"
                    
            finally:
                with self._lock:
                    self._connected = False
                    self._speed = 0.0
                    self._is_boosting = False
                    self._boost_amount = 100
                    self._last_boost_activity_time = 0.0
                    self._prev_boost_amount = None
                
                if sock is not None:
                    try:
                        sock.close()
                    except Exception:
                        pass
            
            retry_count += 1
            if self._running:
                time.sleep(self.RECONNECT_DELAY)
    
    def _parse_packet(self, raw: str):
        """Gelen JSON paketini cozumler.
        
        Gercek format (kesfedildi):
        {
          "Event": "UpdateState",
          "Data": "{\"Players\":[{\"Speed\":81.9, \"Boost\":12, \"bBoosting\":true, ...}], ...}"
        }
        
        DIKKAT: "Data" alani STRING! Icindeki JSON'u tekrar parse etmek gerekiyor.
        Oyuncu verileri Players dizisinin icinde.
        """
        try:
            packet = json.loads(raw)
            
            if not isinstance(packet, dict):
                return
            
            # Sadece UpdateState event'lerini isle
            event = packet.get("Event", "")
            if event != "UpdateState":
                return
            
            data_raw = packet.get("Data", "")
            
            # Data alani STRING olarak geliyor - tekrar parse et
            if isinstance(data_raw, str):
                try:
                    data = json.loads(data_raw)
                except json.JSONDecodeError:
                    return
            elif isinstance(data_raw, dict):
                data = data_raw
            else:
                return
            
            # Players dizisinden kendi oyuncumuzu bul
            players = data.get("Players", [])
            if not players:
                return
            
            # Ilk oyuncu (Shortcut=1 olan veya ilk eleman) bizim arabamiz
            player = players[0]
            for p in players:
                if p.get("Shortcut", 0) == 1:
                    player = p
                    break
            
            # Rocket League'in JSON gondericisi eger deger 0 ise (veya False ise) alani tamamen GIZLER!
            # Yani "Boost" alani json'da yoksa, bu boost'un 0 oldugu anlamina gelir.
            # Delta update degildir, tam state'dir. Sadece default (0) olanlari gondermez.
            speed_raw = float(player.get("Speed", 0.0))
            boost_amount = int(player.get("Boost", 0))  # Yoksa 0'dir!
            
            # km/h -> uu/s donusumu
            speed_uu = speed_raw * self.SPEED_CONVERSION
            
            boosting_flag = self._read_boosting_flag(player)
            boost_is_draining = self._detect_boosting(boost_amount)
            now = time.monotonic()
            boosting = False

            if boosting_flag is True or boost_is_draining:
                boosting = True
                self._last_boost_activity_time = now
            elif (now - self._last_boost_activity_time) <= self.BOOST_ACTIVITY_WINDOW:
                # bBoosting tek karelik dusse bile sesi hemen kesme.
                boosting = True
            
            with self._lock:
                self._speed = speed_uu
                self._speed_raw = speed_raw
                self._is_boosting = boosting
                self._boost_amount = boost_amount
                self._packet_count += 1
            
            # Ilk basarili pakette bilgi ver
            if self._packet_count == 1:
                available_fields = list(player.keys())
                print(f"  [API] Ilk veri paketi alindi!", flush=True)
                print(f"  [API]   Oyuncu: {player.get('Name', '?')}", flush=True)
                print(f"  [API]   Speed={speed_raw:.1f} km/h -> {speed_uu:.0f} uu/s", flush=True)
                print(f"  [API]   Boost={boost_amount}, bBoosting={'bBoosting' in player}", flush=True)
                print(f"  [API]   Tum alanlar: {available_fields}", flush=True)
                
        except (json.JSONDecodeError, ValueError, TypeError, AttributeError) as e:
            if self._packet_count == 0:
                print(f"  [API] JSON parse hatasi: {e}", flush=True)
                print(f"  [API] Ham veri: {raw[:300]}", flush=True)
    
    def _read_boosting_flag(self, player):
        """API'deki bBoosting alanini varsa bool olarak dondurur."""
        if "bBoosting" not in player:
            return None

        value = player["bBoosting"]
        if isinstance(value, bool):
            return value
        if isinstance(value, (int, float)):
            return value != 0
        if isinstance(value, str):
            normalized = value.strip().lower()
            if normalized in {"true", "1", "yes", "on"}:
                return True
            if normalized in {"false", "0", "no", "off", ""}:
                return False
        return bool(value)

    def _detect_boosting(self, current_boost):
        """bBoosting alanina ek olarak boost'un gercekten azaldigini kontrol eder."""
        prev = self._prev_boost_amount
        self._prev_boost_amount = current_boost

        if prev is None:
            return False

        # Boost azaliyorsa, oyuncu boost kullaniyor demektir.
        return current_boost < prev
