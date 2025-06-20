import os
import subprocess

import psutil


class XrayManager:
    def __init__(self, executable_path: str, config_path: str) -> None:
        self.executable_path: str = executable_path
        self.config_path: str = config_path

        self._process: psutil.Popen | None = None

    def is_running(self) -> bool:
        return self._process is not None and self._process.is_running()

    def start(self) -> bool:
        if self.is_running():
            return True

        if not os.path.isfile(self.config_path):
            return False

        try:
            self._process = psutil.Popen(
                [self.executable_path, "-c", self.config_path], creationflags=subprocess.CREATE_NO_WINDOW
            )
            return True
        except Exception:
            self._process = None
            return False

    def stop(self) -> None:
        if not self.is_running():
            return

        self._process.kill()
        self._process = None
