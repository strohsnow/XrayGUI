from typing import Any

from PySide6.QtCore import QObject
from PySide6.QtGui import QAction, QIcon
from PySide6.QtWidgets import QMenu, QSystemTrayIcon, QWidget

from config import APP_NAME
from utils.i18n import tr


class Tray(QObject):
    def __init__(self, parent: QWidget, icon: QIcon) -> None:
        super().__init__(parent)
        self.parent = parent
        self.icon = icon

        self.tray = QSystemTrayIcon(self.icon, self.parent)
        self.tray.setToolTip(APP_NAME)
        self.tray.activated.connect(self._tray_click)

        self.show_action = QAction(tr("Show"), self.parent, triggered=self.parent.show)
        self.hide_action = QAction(tr("Hide"), self.parent, triggered=self.parent.hide)

        self.toggle_xray_action = QAction(self.parent)
        self.toggle_tun_action = QAction(self.parent)
        self.toggle_system_proxy_action = QAction(self.parent)

        self.server_menu = QMenu(tr("Select server"), self.parent)
        self.server_actions = []

        self._setup_menu()
        self.tray.show()

    def _setup_menu(self) -> None:
        tray_menu = QMenu()

        tray_menu.addAction(self.show_action)
        tray_menu.addAction(self.hide_action)
        tray_menu.addSeparator()

        tray_menu.addAction(self.toggle_xray_action)
        tray_menu.addAction(self.toggle_tun_action)
        tray_menu.addAction(self.toggle_system_proxy_action)
        tray_menu.addSeparator()

        tray_menu.addMenu(self.server_menu)
        tray_menu.addSeparator()

        action_quit = QAction(tr("Quit"), self.parent, triggered=self.parent._quit)
        tray_menu.addAction(action_quit)

        self.tray.setContextMenu(tray_menu)

    def _tray_click(self, reason: QSystemTrayIcon.ActivationReason) -> None:
        if reason == QSystemTrayIcon.ActivationReason.Context:
            return

        if self.parent.isVisible():
            self.parent.hide()
        else:
            self.parent.show()

    def update_action_visibility(self) -> None:
        self.show_action.setVisible(not self.parent.isVisible())
        self.hide_action.setVisible(self.parent.isVisible())

    def update_server_menu(self, servers: list[dict[str, Any]], current_server: str | None = None) -> None:
        self.server_menu.clear()
        self.server_actions.clear()

        if not servers:
            action = QAction(tr("No servers available"), self.parent)
            action.setEnabled(False)
            self.server_menu.addAction(action)
            return

        for server in servers:
            remark = server.get("remarks", "No remark")
            action = QAction(remark, self.parent, checkable=True)
            action.setChecked(remark == current_server)
            action.triggered.connect(lambda checked, r=remark: self.parent._select_server(r))
            self.server_actions.append(action)
            self.server_menu.addAction(action)

    def update_xray_action(self, running: bool) -> None:
        self.toggle_xray_action.setText(f"{tr('Stop') if running else tr('Start')} VPN")

    def update_tun_action(self, enabled: bool) -> None:
        self.toggle_tun_action.setText(f"{tr('Disable') if enabled else tr('Enable')} TUN")

    def update_system_proxy_action(self, enabled: bool) -> None:
        self.toggle_system_proxy_action.setText(f"{tr('Disable') if enabled else tr('Enable')} {tr('system proxy')}")
