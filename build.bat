@echo off
echo Building Alpha Boost Engine...
REM Ikon var mi kontrol et
if exist "icon.png" (
    echo Ikon bulundu! Exe'ye ekleniyor...
    REM PyInstaller icin .ico lazim olabilir ama .png de bazen calisir. Biz yine de arayuz ikonunu veri olarak ekleyelim.
    pyinstaller --noconfirm --onefile --noconsole --name "AlphaBoostEngine" --add-data "assets;assets" --add-data "icon.png;." main.py
) else (
    echo Ikon bulunamadi. Varsayilan ikon ile derleniyor...
    pyinstaller --noconfirm --onefile --noconsole --name "AlphaBoostEngine" --add-data "assets;assets" main.py
)
echo Build complete! Check the 'dist' folder.
pause
