import os
import subprocess


class XrayManager:
    def __init__(self, xray_path: str, config_path: str) -> None:
        self.xray_path: str = xray_path
        self.config_path: str = config_path

        self.xray_process: subprocess.Popen | None = None

    def is_running(self) -> bool:
        return self.xray_process is not None and self.xray_process.poll() is None

    def start(self) -> bool:
        if not os.path.isfile(self.config_path):
            return False

        try:
            if not self.is_running():
                self.xray_process = subprocess.Popen(
                    [self.xray_path, "-c", self.config_path],
                    creationflags=subprocess.CREATE_NO_WINDOW,
                )
                return True
        except Exception:
            return False
        return False

    def stop(self) -> bool:
        try:
            if self.is_running():
                self.xray_process.terminate()
                self.xray_process.wait(5)
                self.xray_process = None
            return True
        except Exception:
            return False
