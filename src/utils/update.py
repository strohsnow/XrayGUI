import requests
from packaging import version

from config import APP_NAME, GITHUB_API_LATEST_RELEASE, GITHUB_RELEASES_PAGE


def get_latest_version() -> tuple[str | None, str]:
    try:
        response = requests.get(GITHUB_API_LATEST_RELEASE)
        response.raise_for_status()
        data = response.json()
    except Exception:
        return None, GITHUB_RELEASES_PAGE

    tag = data.get("tag_name")
    if tag and tag.startswith("v"):
        tag = tag.removeprefix("v")

    download_url = GITHUB_RELEASES_PAGE
    for asset in data.get("assets", []):
        if asset.get("name", "").lower() == f"{APP_NAME.lower()}.exe":
            download_url = asset.get("browser_download_url", download_url)
            break

    return tag, download_url


def is_newer_version(current: str, remote: str) -> bool:
    try:
        return version.parse(remote) > version.parse(current)
    except Exception:
        return False
