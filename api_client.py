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
        self._speed = 0.0
        self._is_boosting = False
        self._connected = False
        self._last_error = ""
        self._packet_count = 0
        
        self._thread = None
        self._running = False
    
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
                
                while self._running:
                    try:
                        data = sock.recv(self.BUFFER_SIZE)
                        if not data:
                            print("  [API] Baglanti kapandi (bos veri)", flush=True)
                            break
                        
                        buffer += data.decode("utf-8", errors="replace")
                        
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
        
        Beklenen formatlar:
        1) {"Event": "UpdateState", "Data": {"Speed": ..., "Boost": ..., "bBoosting": ...}}
        2) {"Speed": ..., "Boost": ..., "bBoosting": ...}
        """
        try:
            packet = json.loads(raw)
            
            # Rocket League resmi API: veriler "Data" anahtarinin icinde olabilir
            if isinstance(packet, dict) and "Data" in packet:
                data = packet["Data"]
            else:
                data = packet
            
            if not isinstance(data, dict):
                return
            
            # Hiz ve boost bilgisini al
            speed = float(data.get("Speed", data.get("speed", 0.0)))
            boosting = bool(data.get("bBoosting", data.get("boosting", False)))
            
            with self._lock:
                self._speed = speed
                self._is_boosting = boosting
                self._packet_count += 1
            
            # Ilk basarili pakette bilgi ver
            if self._packet_count == 1:
                print(f"  [API] Ilk veri paketi alindi! Speed={speed:.1f}, Boosting={boosting}", flush=True)
                
        except (json.JSONDecodeError, ValueError, TypeError, AttributeError) as e:
            # Ilk parse hatasini goster (debug icin)
            if self._packet_count == 0:
                print(f"  [API] JSON parse hatasi: {e}", flush=True)
                print(f"  [API] Ham veri: {raw[:200]}", flush=True)
