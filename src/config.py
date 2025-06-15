import os
from pathlib import Path

APP_ROOT = Path(__file__).resolve().parent

_ENV_APPDATA = os.getenv("APPDATA")
if _ENV_APPDATA:
    APPDATA_ROOT = Path(_ENV_APPDATA)
elif (Path.home() / "AppData" / "Roaming").exists():
    APPDATA_ROOT = Path.home() / "AppData" / "Roaming"
else:
    APPDATA_ROOT = Path.home() / ".config"

BIN_DIR = APP_ROOT / "bin"
ASSET_DIR = APP_ROOT / "assets"
APPDATA_DIR = APPDATA_ROOT / "XrayGUI"
CONFIG_DIR = APPDATA_DIR / "config"
LOG_DIR = APPDATA_DIR / "logs"

XRAY_PATH = str(BIN_DIR / "xray.exe")
ICON_PATH = str(ASSET_DIR / "icon.ico")
CONFIGS_PATH = str(CONFIG_DIR / "configs.json")
CONFIG_PATH = str(CONFIG_DIR / "config.json")
SUB_PATH = str(CONFIG_DIR / "sub.txt")

USER_AGENT = "Happ/XrayGUI/1.2"
PROXY_IP_ADDR = "127.0.0.1"
PROXY_PORT = 2080
SOCKET_NAME = "XrayGUI"

CONFIG_DIR.mkdir(parents=True, exist_ok=True)
