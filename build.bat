@echo off
echo Building Alpha Boost Engine...
if exist "icon.ico" (
    echo Ikon bulundu! Exe'ye ekleniyor...
    pyinstaller --noconfirm --onefile --noconsole --name "AlphaBoostEngine" --icon="icon.ico" --add-data "assets;assets" --add-data "icon.ico;." main.py
) else (
    echo Ikon bulunamadi. Varsayilan ikon ile derleniyor...
    pyinstaller --noconfirm --onefile --noconsole --name "AlphaBoostEngine" --add-data "assets;assets" main.py
)
echo Build complete! Check the 'dist' folder.
pause
