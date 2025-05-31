import sys
from pathlib import Path

APP_DIR = Path(sys.argv[0]).resolve().parent
BIN_DIR = APP_DIR / "bin"
CONFIG_DIR = APP_DIR / "config"

XRAY_EXE = str(BIN_DIR / "xray.exe")
NSSM_EXE = str(BIN_DIR / "nssm.exe")

CONFIGS_JSON = str(CONFIG_DIR / "configs.json")
CONFIG_JSON = str(CONFIG_DIR / "config.json")
SUB_TXT = str(CONFIG_DIR / "sub.txt")

XRAY_SERVICE = "XrayGUI"
FIREWALL_RULE = "XrayGUI"
USER_AGENT = "Happ/XrayGUI/1.0"

PROXY_IP_ADDR = "127.0.0.1"
PROXY_PORT = 2080
