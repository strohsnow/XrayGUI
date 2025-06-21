import os
from pathlib import Path

APP_ROOT = Path(__file__).resolve().parent

APPDATA_ROOT = Path(os.getenv("APPDATA") or Path.home() / "AppData" / "Roaming")
LOCALAPPDATA_ROOT = Path(os.getenv("LOCALAPPDATA") or Path.home() / "AppData" / "Local")

ASSET_DIR = APP_ROOT / "assets"
BIN_DIR = APP_ROOT / "bin"
APPDATA_DIR = APPDATA_ROOT / "XrayGUI"
CONFIG_DIR = APPDATA_DIR / "config"
LOG_DIR = APPDATA_DIR / "log"
DISCORD_DIR = LOCALAPPDATA_ROOT / "Discord"

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
APP_VERSION = "1.7"
USER_AGENT = f"Happ/{APP_NAME}/{APP_VERSION}"

PROXY_IP_ADDR = "127.0.0.1"
PROXY_PORT = 2080

DISCORD_PROXY_DLLS = ["DWrite.dll", "force-proxy.dll"]
DISCORD_PROXY_CONFIG = "proxy.txt"

GITHUB_RELEASES_PAGE = "https://github.com/strohsnow/XrayGUI/releases"
GITHUB_API_LATEST_RELEASE = "https://api.github.com/repos/strohsnow/XrayGUI/releases/latest"
