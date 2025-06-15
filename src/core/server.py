import base64
import json
import os
import platform
import winreg
from typing import Any

import requests
import wmi


class ServerManager:
    def __init__(self, user_agent: str, subscription_path: str, servers_path: str, current_server_path: str) -> None:
        self.user_agent: str = user_agent

        self.subscription_path: str = subscription_path
        self.servers_path: str = servers_path
        self.current_server_path: str = current_server_path

        self.subscription_url: str | None = None
        self.servers: list[dict[str, Any]] = []
        self.current_server: str | None = None

        self._load_subscription_url()
        self._load_servers()
        self._load_current_server()

    def _load_subscription_url(self) -> None:
        if os.path.isfile(self.subscription_path):
            with open(self.subscription_path, "r", encoding="utf-8") as f:
                self.subscription_url = f.read().strip()

    def _load_servers(self) -> None:
        if os.path.isfile(self.servers_path):
            with open(self.servers_path, "r", encoding="utf-8") as f:
                self.servers = json.load(f)

    def _load_current_server(self) -> None:
        if os.path.isfile(self.current_server_path):
            with open(self.current_server_path, "r", encoding="utf-8") as f:
                self.current_server = json.load(f).get("remarks", "No remark")

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
            "x-hwid": ServerManager._get_machine_guid(),
            "x-device-os": platform.system(),
            "x-ver-os": platform.version(),
            "x-device-model": ServerManager._get_device_model(),
        }
        return hwid_headers

    def import_subscription(self, url: str) -> None:
        headers = ServerManager._get_hwid_headers()
        headers.update({"User-Agent": self.user_agent})

        response = requests.get(url.rstrip("/") + "/json", headers=headers)
        response.raise_for_status()

        announce = response.headers.get("Announce", "")
        if announce:
            announce = announce.removeprefix("base64:")
            raise Exception(f"{base64.b64decode(announce).decode('utf-8')}")

        self.servers = response.json()
        with open(self.servers_path, "w", encoding="utf-8") as f:
            json.dump(self.servers, f, ensure_ascii=False, indent=2)

        with open(self.subscription_path, "w", encoding="utf-8") as f:
            f.write(url)

    def select_server(self, remark: str) -> bool:
        if not self.servers:
            return False

        for server in self.servers:
            if server.get("remarks", "No remark") == remark:
                with open(self.current_server_path, "w", encoding="utf-8") as f:
                    json.dump(server, f, ensure_ascii=False, indent=2)
                self.current_server = remark
                return True
        return False
