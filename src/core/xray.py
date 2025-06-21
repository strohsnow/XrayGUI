import os
import subprocess

import psutil


class XrayManager:
    def __init__(self, executable_path: str, config_path: str, log_dir: str) -> None:
        self.executable_path: str = executable_path
        self.config_path: str = config_path
        self.log_dir: str = log_dir

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
                [self.executable_path, "run", "-c", self.config_path],
                cwd=self.log_dir,
                creationflags=subprocess.CREATE_NO_WINDOW,
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
