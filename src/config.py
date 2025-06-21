import os
from pathlib import Path

APP_ROOT = Path(__file__).resolve().parent

_ENV_APPDATA = os.getenv("APPDATA")
if _ENV_APPDATA:
    APPDATA_ROOT = Path(_ENV_APPDATA)
else:
    APPDATA_ROOT = Path.home() / "AppData" / "Roaming"

ASSET_DIR = APP_ROOT / "assets"
BIN_DIR = APP_ROOT / "bin"
APPDATA_DIR = APPDATA_ROOT / "XrayGUI"
CONFIG_DIR = APPDATA_DIR / "config"
LOG_DIR = APPDATA_DIR / "log"

CONFIG_DIR.mkdir(parents=True, exist_ok=True)
LOG_DIR.mkdir(parents=True, exist_ok=True)

ICON_PATH = str(ASSET_DIR / "icon.ico")
SUBSCRIPTION_PATH = str(CONFIG_DIR / "subscription.txt")
XRAY_PATH = str(BIN_DIR / "xray.exe")
XRAY_CONFIGS_PATH = str(CONFIG_DIR / "configs.json")
XRAY_CONFIG_PATH = str(CONFIG_DIR / "config.json")
XRAY_LOG_PATH = str(LOG_DIR)
TUN_PATH = str(BIN_DIR / "mihomo.exe")
TUN_CONFIG_PATH = str(CONFIG_DIR / "config.yaml")
TUN_LOG_PATH = str(LOG_DIR / "tun.log")

APP_NAME = "XrayGUI"
APP_VERSION = "1.6"
USER_AGENT = f"Happ/{APP_NAME}/{APP_VERSION}"
PROXY_IP_ADDR = "127.0.0.1"
PROXY_PORT = 2080

GITHUB_RELEASES_PAGE = "https://github.com/strohsnow/XrayGUI/releases"
GITHUB_API_LATEST_RELEASE = "https://api.github.com/repos/strohsnow/XrayGUI/releases/latest"
