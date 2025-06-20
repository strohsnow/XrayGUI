import os

import psutil
import win32com.shell.shell as shell
import win32con
import win32process
from win32com.shell import shellcon


class TunManager:
    def __init__(self, executable_path: str, config_path: str) -> None:
        self.executable_path: str = executable_path
        self.config_path: str = config_path

        self._process: psutil.Process | None = None

    def is_running(self) -> bool:
        return self._process is not None and self._process.is_running()

    def start(self) -> bool:
        if self.is_running():
            return True

        if not os.path.isfile(self.config_path):
            return False

        try:
            info = shell.ShellExecuteEx(
                fMask=shellcon.SEE_MASK_NOCLOSEPROCESS,
                lpVerb="runas",
                lpFile=self.executable_path,
                lpParameters=f'-d "{os.path.dirname(self.executable_path)}" -f "{self.config_path}"',
                lpDirectory=os.path.dirname(self.executable_path),
                nShow=win32con.SW_HIDE,
            )
            handle = info["hProcess"]
            pid = win32process.GetProcessId(handle)
            self._process = psutil.Process(pid)
            return True
        except Exception:
            self._process = None
            return False

    def stop(self) -> None:
        if not self.is_running():
            return

        self._process.kill()
        self._process = None
