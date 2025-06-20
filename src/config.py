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

ASSET_DIR = APP_ROOT / "assets"
BIN_DIR = APP_ROOT / "bin"
APPDATA_DIR = APPDATA_ROOT / "XrayGUI"
CONFIG_DIR = APPDATA_DIR / "config"
LOG_DIR = APPDATA_DIR / "logs"

ICON_PATH = str(ASSET_DIR / "icon.ico")
SUBSCRIPTION_PATH = str(CONFIG_DIR / "subscription.txt")
XRAY_PATH = str(BIN_DIR / "xray.exe")
XRAY_CONFIGS_PATH = str(CONFIG_DIR / "configs.json")
XRAY_CONFIG_PATH = str(CONFIG_DIR / "config.json")
TUN_PATH = str(BIN_DIR / "mihomo.exe")
TUN_CONFIG_PATH = str(CONFIG_DIR / "config.yaml")

USER_AGENT = "Happ/XrayGUI/1.3"
PROXY_IP_ADDR = "127.0.0.1"
PROXY_PORT = 2080
SOCKET_NAME = "XrayGUI"

CONFIG_DIR.mkdir(parents=True, exist_ok=True)
