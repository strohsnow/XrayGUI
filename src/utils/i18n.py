import locale

_TRANSLATIONS: dict[str, dict[str, str]] = {
    "ru": {
        "Status": "Статус",
        "Running": "Запущен",
        "Stopped": "Остановлен",
        "Server": "Сервер",
        "Not selected": "Не выбран",
        "No remark": "Без названия",
        "Start": "Запустить",
        "Failed to start VPN": "Не удалось запустить VPN",
        "Stop": "Остановить",
        "Select server": "Выбрать сервер",
        "Choose a server:": "Выберите сервер:",
        "Enable": "Включить",
        "Failed to start TUN": "Не удалось запустить TUN",
        "Disable": "Отключить",
        "system proxy": "системный прокси",
        "Discord proxy": "Discord прокси",
        "Failed to enable Discord proxy": "Не удалось включить Discord прокси",
        "Import subscription": "Импортировать подписку",
        "Enter subscription URL:": "Введите URL подписки:",
        "Subscription imported successfully": "Подписка успешно импортирована",
        "Failed to import subscription:\n{error}": "Не удалось импортировать подписку:\n{error}",
        "Update subscription": "Обновить подписку",
        "Subscription updated successfully": "Подписка успешно обновлена",
        "Failed to update subscription:\n{error}": "Не удалось обновить подписку:\n{error}",
        "Import a subscription first": "Сначала импортируйте подписку",
        "Select a server first": "Сначала выберите сервер",
        "Update available": "Доступно обновление",
        "A new version {version} is available.\nWould you like to download it now?": "Доступна новая версия {version}.\nХотите скачать её сейчас?",
        "Success": "Успех",
        "Error": "Ошибка",
        "Show": "Показать",
        "Hide": "Скрыть",
        "No servers available": "Нет доступных серверов",
        "Quit": "Выход",
    },
}


def _detect_system_language() -> str:
    loc, _ = locale.getdefaultlocale() or (None, None)
    if loc and loc.lower().startswith("ru"):
        return "ru"
    return "en"


_current_language: str = _detect_system_language()


def get_current_language() -> str:
    return _current_language


def tr(text: str, **kwargs: str) -> str:
    translated = _TRANSLATIONS.get(_current_language, {}).get(text, text)
    if kwargs:
        return translated.format(**kwargs)
    return translated
