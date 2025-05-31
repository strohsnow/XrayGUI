import os
import subprocess


def add_rule(rule_name: str, exe_path: str) -> None:
    exe_path = os.path.abspath(exe_path)
    subprocess.run(
        [
            "netsh",
            "advfirewall",
            "firewall",
            "add",
            "rule",
            f"name={rule_name}",
            "dir=in",
            "action=allow",
            f"program={exe_path}",
            "enable=yes",
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=True,
        creationflags=subprocess.CREATE_NO_WINDOW,
    )


def delete_rule(rule_name: str) -> None:
    subprocess.run(
        ["netsh", "advfirewall", "firewall", "delete", "rule", f"name={rule_name}"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=True,
        creationflags=subprocess.CREATE_NO_WINDOW,
    )
