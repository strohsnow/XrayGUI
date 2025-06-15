pyinstaller `
  --clean `
  --onedir `
  --noconsole `
  --name "XrayGUI" `
  --icon "assets\icon.ico" `
  --add-data "assets;assets" `
  --add-data "bin;bin" `
  --add-binary "bin\xray.exe;bin" `
  src\app.py
