import os
import subprocess


def install_service(
    nssm_path: str, service_name: str, exe_path: str, args: list[str] | None = None
) -> None:
    if not os.path.isfile(nssm_path):
        raise FileNotFoundError(f"NSSM not found at '{nssm_path}'")
    if not os.path.isfile(exe_path):
        raise FileNotFoundError(f"Executable not found at '{exe_path}'")

    cmd = [nssm_path, "install", service_name, exe_path]
    if args:
        cmd.extend(args)

    subprocess.run(
        cmd,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=True,
        creationflags=subprocess.CREATE_NO_WINDOW,
    )
    subprocess.run(
        [nssm_path, "set", service_name, "Start", "SERVICE_AUTO_START"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=True,
        creationflags=subprocess.CREATE_NO_WINDOW,
    )


def remove_service(nssm_path: str, service_name: str) -> None:
    if not os.path.isfile(nssm_path):
        raise FileNotFoundError(f"NSSM not found at '{nssm_path}'")

    subprocess.run(
        [nssm_path, "remove", service_name, "confirm"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=True,
        creationflags=subprocess.CREATE_NO_WINDOW,
    )


def start_service(nssm_path: str, service_name: str) -> None:
    if not os.path.isfile(nssm_path):
        raise FileNotFoundError(f"NSSM not found at '{nssm_path}'")

    subprocess.run(
        [nssm_path, "start", service_name],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=True,
        creationflags=subprocess.CREATE_NO_WINDOW,
    )


def stop_service(nssm_path: str, service_name: str) -> None:
    if not os.path.isfile(nssm_path):
        raise FileNotFoundError(f"NSSM not found at '{nssm_path}'")

    subprocess.run(
        [nssm_path, "stop", service_name],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=True,
        creationflags=subprocess.CREATE_NO_WINDOW,
    )


def restart_service(nssm_path: str, service_name: str) -> None:
    if not os.path.isfile(nssm_path):
        raise FileNotFoundError(f"NSSM not found at '{nssm_path}'")

    subprocess.run(
        [nssm_path, "restart", service_name],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=True,
        creationflags=subprocess.CREATE_NO_WINDOW,
    )


def service_running(nssm_path: str, service_name: str) -> bool:
    if not os.path.isfile(nssm_path):
        raise FileNotFoundError(f"NSSM not found at '{nssm_path}'")

    try:
        result = subprocess.run(
            [nssm_path, "status", service_name],
            check=True,
            capture_output=True,
            text=True,
        )
        return result.stdout.strip() == "SERVICE_RUNNING"
    except subprocess.CalledProcessError:
        return False
