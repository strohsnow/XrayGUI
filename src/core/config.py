import base64
import json
import os
import platform
import winreg
from typing import Any

import requests
import wmi


class ConfigManager:
    def __init__(
        self,
        user_agent: str,
        subscription_path: str,
        xray_configs_path: str,
        xray_config_path: str,
        tun_config_path: str,
    ) -> None:
        self.user_agent: str = user_agent

        self.subscription_path: str = subscription_path
        self.xray_configs_path: str = xray_configs_path
        self.xray_config_path: str = xray_config_path
        self.tun_config_path: str = tun_config_path

        self.subscription_url: str | None = None
        self.xray_configs: list[dict[str, Any]] = []
        self.current_remark: str | None = None

        self._load_subscription_url()
        self._load_xray_configs()
        self._load_xray_config()

    def _load_subscription_url(self) -> None:
        if os.path.isfile(self.subscription_path):
            with open(self.subscription_path, "r", encoding="utf-8") as f:
                self.subscription_url = f.read().strip()

    def _load_xray_configs(self) -> None:
        if os.path.isfile(self.xray_configs_path):
            with open(self.xray_configs_path, "r", encoding="utf-8") as f:
                self.xray_configs = json.load(f)

    def _load_xray_config(self) -> None:
        if os.path.isfile(self.xray_config_path):
            with open(self.xray_config_path, "r", encoding="utf-8") as f:
                self.current_remark = json.load(f).get("remarks", "No remark")

    @staticmethod
    def _get_machine_guid() -> str:
        key = r"SOFTWARE\Microsoft\Cryptography"
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key) as key:
            guid, _ = winreg.QueryValueEx(key, "MachineGuid")
        return guid

    @staticmethod
    def _get_device_model() -> str:
        c = wmi.WMI()
        sysinfo = c.Win32_ComputerSystem()[0]
        return sysinfo.Model

    @staticmethod
    def _get_hwid_headers() -> dict[str, str]:
        hwid_headers = {
            "x-hwid": ConfigManager._get_machine_guid(),
            "x-device-os": platform.system(),
            "x-ver-os": platform.version(),
            "x-device-model": ConfigManager._get_device_model(),
        }
        return hwid_headers

    def import_configs(self, url: str) -> None:
        headers = ConfigManager._get_hwid_headers()
        headers.update({"User-Agent": self.user_agent})

        response = requests.get(url.rstrip("/") + "/json", headers=headers)
        response.raise_for_status()

        announce = response.headers.get("Announce", "")
        if announce:
            announce = announce.removeprefix("base64:")
            raise Exception(f"{base64.b64decode(announce).decode('utf-8')}")

        self.xray_configs = response.json()
        with open(self.xray_configs_path, "w", encoding="utf-8") as f:
            json.dump(self.xray_configs, f, ensure_ascii=False, indent=2)

        if not self.current_remark:
            self.current_remark = self.xray_configs[0].get("remarks", "No remark")
        self.select_config(self.current_remark)

        response = requests.get(url.rstrip("/") + "/mihomo", headers=headers)
        response.raise_for_status()

        with open(self.tun_config_path, "w", encoding="utf-8") as f:
            f.write(response.text)

        self.subscription_url = url
        with open(self.subscription_path, "w", encoding="utf-8") as f:
            f.write(self.subscription_url)

    def select_config(self, remark: str) -> bool:
        if not self.xray_configs:
            return False

        for config in self.xray_configs:
            if config.get("remarks", "No remark") == remark:
                with open(self.xray_config_path, "w", encoding="utf-8") as f:
                    json.dump(config, f, ensure_ascii=False, indent=2)
                self.current_remark = remark
                return True
        return False
