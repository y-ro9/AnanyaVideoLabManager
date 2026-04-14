@echo off
echo Installing required packages...
pip install customtkinter Pillow reportlab openpyxl pyinstaller

echo Building executable...
pyinstaller --onefile --windowed --name="AnanyaVideoLabManager" --icon=assets/logo.ico --add-data="assets;assets" main.py

echo Build complete! Check 'dist' folder for the executable.
pause