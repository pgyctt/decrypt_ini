call .venv\Scripts\activate
pyinstaller -F -w -i "assets\icon.ico" decrypt_ini.py --splash "assets\loading.png"
pause