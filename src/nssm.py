import os
import subprocess


class NSSM:
    def __init__(self, nssm_path: str, service_name: str):
        if not os.path.isfile(nssm_path):
            raise FileNotFoundError(f"NSSM not found at '{nssm_path}'")

        self.nssm_path: str = nssm_path
        self.service_name: str = service_name

    def install(self, exe_path: str, args: list[str] | None = None) -> None:
        if not os.path.isfile(exe_path):
            raise FileNotFoundError(f"Executable not found at '{exe_path}'")

        cmd = [self.nssm_path, "install", self.service_name, exe_path]
        if args:
            cmd.extend(args)

        subprocess.run(
            cmd,
            check=True,
            creationflags=subprocess.CREATE_NO_WINDOW,
        )
        subprocess.run(
            [self.nssm_path, "set", self.service_name, "Start", "SERVICE_AUTO_START"],
            check=True,
            creationflags=subprocess.CREATE_NO_WINDOW,
        )

    def remove(self) -> None:
        subprocess.run(
            [self.nssm_path, "remove", self.service_name, "confirm"],
            check=True,
            creationflags=subprocess.CREATE_NO_WINDOW,
        )

    def start(self) -> None:
        subprocess.run(
            [self.nssm_path, "start", self.service_name],
            check=True,
            creationflags=subprocess.CREATE_NO_WINDOW,
        )

    def stop(self) -> None:
        subprocess.run(
            [self.nssm_path, "stop", self.service_name],
            check=True,
            creationflags=subprocess.CREATE_NO_WINDOW,
        )

    def restart(self) -> None:
        subprocess.run(
            [self.nssm_path, "restart", self.service_name],
            check=True,
            creationflags=subprocess.CREATE_NO_WINDOW,
        )

    def service_running(self) -> bool:
        try:
            result = subprocess.run(
                [self.nssm_path, "status", self.service_name],
                check=True,
                capture_output=True,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW,
            )
            return result.stdout.strip() == "SERVICE_RUNNING"
        except subprocess.CalledProcessError:
            return False
