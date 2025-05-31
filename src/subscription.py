import base64
import json
import platform
import winreg

import requests
import wmi

import config


def _get_machine_guid() -> str:
    reg_path = r"SOFTWARE\Microsoft\Cryptography"
    with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, reg_path) as key:
        guid, _ = winreg.QueryValueEx(key, "MachineGuid")
    return guid


def _get_device_model() -> str:
    c = wmi.WMI()
    sysinfo = c.Win32_ComputerSystem()[0]
    return sysinfo.Model


def _get_hwid_headers() -> dict:
    hwid_headers = {
        "x-hwid": _get_machine_guid(),
        "x-device-os": platform.system(),
        "x-ver-os": platform.version(),
        "x-device-model": _get_device_model(),
    }
    return hwid_headers


def get_config_json(url: str, config_path: str) -> None:
    headers = _get_hwid_headers()
    headers.update({"User-Agent": config.USER_AGENT})

    url = url.rstrip("/") + "/json"
    response = requests.get(url, headers=headers)
    response.raise_for_status()

    announce = response.headers.get("Announce", "")
    if announce:
        announce = announce.removeprefix("base64:")
        raise Exception(f"{base64.b64decode(announce).decode('utf-8')}")

    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(response.json(), f, ensure_ascii=False, indent=2)
