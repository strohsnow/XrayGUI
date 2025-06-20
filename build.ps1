pyinstaller `
  --noconfirm `
  --clean `
  --onedir `
  --noconsole `
  --name "XrayGUI" `
  --icon "assets\icon.ico" `
  --add-data "assets;assets" `
  --add-data "bin;bin" `
  --add-binary "bin\xray.exe;bin" `
  --add-binary "bin\mihomo.exe;bin" `
  src\app.py
