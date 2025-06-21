import ctypes
import winreg


class SystemProxyManager:
    KEY: str = r"Software\Microsoft\Windows\CurrentVersion\Internet Settings"

    def __init__(self, ip_addr: str, port: int) -> None:
        self.ip_addr: str = ip_addr
        self.port: int = port

    @staticmethod
    def _refresh(self) -> None:
        ctypes.windll.Wininet.InternetSetOptionW(0, 37, 0, 0)
        ctypes.windll.Wininet.InternetSetOptionW(0, 39, 0, 0)

    def set_server(self) -> None:
        proxy_server = f"{self.ip_addr}:{self.port}"
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, self.KEY, 0, winreg.KEY_ALL_ACCESS) as key:
            winreg.SetValueEx(key, "ProxyServer", 0, winreg.REG_SZ, proxy_server)

        self._refresh()

    def delete_server(self) -> None:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, self.KEY, 0, winreg.KEY_ALL_ACCESS) as key:
            try:
                winreg.DeleteValue(key, "ProxyServer")
            except FileNotFoundError:
                pass

        self._refresh()

    def set_enable(self, enable: bool) -> None:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, self.KEY, 0, winreg.KEY_ALL_ACCESS) as key:
            if enable and not self.server_set():
                return
            winreg.SetValueEx(key, "ProxyEnable", 0, winreg.REG_DWORD, enable)

        self._refresh()

    def server_set(self) -> bool:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, self.KEY) as key:
            try:
                server, _ = winreg.QueryValueEx(key, "ProxyServer")
                return server == f"{self.ip_addr}:{self.port}"
            except FileNotFoundError:
                return False

    def enable_set(self) -> bool:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, self.KEY) as key:
            try:
                enabled, _ = winreg.QueryValueEx(key, "ProxyEnable")
                return bool(enabled)
            except FileNotFoundError:
                return False
