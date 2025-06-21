import shutil
import subprocess
from pathlib import Path

import psutil


class DiscordProxyManager:
    def __init__(
        self,
        discord_dir: Path,
        dlls_dir: Path,
        proxy_dlls: list[str],
        proxy_config: str,
        proxy_ip_addr: str,
        proxy_port: int,
    ) -> None:
        self.discord_dir: Path = discord_dir
        self.dlls_dir: Path = dlls_dir
        self.proxy_dlls: list[str] = proxy_dlls
        self.proxy_config: str = proxy_config
        self.proxy_ip_addr: str = proxy_ip_addr
        self.proxy_port: int = proxy_port

    def is_enabled(self) -> bool:
        app_dir = self._latest_app_dir()
        if app_dir is None:
            return False

        for name in (*self.proxy_dlls, self.proxy_config):
            if not (app_dir / name).is_file():
                return False
        return True

    def enable(self) -> bool:
        app_dir = self._latest_app_dir()
        if app_dir is None:
            return False

        exe_path = self._kill_discord()

        try:
            for dll in self.proxy_dlls:
                shutil.copy2(self.dlls_dir / dll, app_dir / dll)

            with open(app_dir / self.proxy_config, "w", encoding="utf-8") as f:
                f.write(f"SOCKS5_PROXY_ADDRESS={self.proxy_ip_addr}\n")
                f.write(f"SOCKS5_PROXY_PORT={self.proxy_port}\n")
        except Exception:
            return False

        self._start_discord(exe_path)
        return True

    def disable(self) -> None:
        app_dir = self._latest_app_dir()
        if app_dir is None:
            return

        self._kill_discord()

        for name in (*self.proxy_dlls, self.proxy_config):
            try:
                (app_dir / name).unlink(missing_ok=True)
            except Exception:
                pass

    def _latest_app_dir(self) -> Path | None:
        if not self.discord_dir.exists():
            return None

        app_dirs = [d for d in self.discord_dir.iterdir() if d.is_dir() and d.name.startswith("app-")]
        if not app_dirs:
            return None

        app_dirs.sort(key=lambda d: d.name.replace("app-", ""), reverse=True)
        return app_dirs[0]

    def _start_discord(self, exe_path: str | None = None) -> None:
        if exe_path and Path(exe_path).exists():
            try:
                subprocess.Popen(exe_path, cwd=str(Path(exe_path).parent), creationflags=subprocess.CREATE_NO_WINDOW)
                return
            except Exception:
                pass

        update_exe = self.discord_dir / "Update.exe"
        if update_exe.exists():
            try:
                subprocess.Popen(
                    [str(update_exe), "--processStart", "Discord.exe"], creationflags=subprocess.CREATE_NO_WINDOW
                )
            except Exception:
                pass

    @staticmethod
    def _kill_discord() -> str | None:
        exe_path: str | None = None

        discord_procs: list[psutil.Process] = []
        for proc in psutil.process_iter(["name", "exe"]):
            try:
                if proc.info["name"] and proc.info["name"].lower() == "discord.exe":
                    if exe_path is None:
                        exe_path = proc.info.get("exe")
                    discord_procs.append(proc)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        if not discord_procs:
            return exe_path

        for proc in discord_procs:
            try:
                proc.kill()
            except Exception:
                pass
        psutil.wait_procs(discord_procs, timeout=5)

        return exe_path
