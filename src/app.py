import json
import sys
import webbrowser

from PySide6.QtCore import QEvent
from PySide6.QtGui import QIcon
from PySide6.QtNetwork import QLocalServer
from PySide6.QtWidgets import (
    QApplication,
    QFrame,
    QHBoxLayout,
    QInputDialog,
    QLabel,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from config import (
    APP_NAME,
    APP_VERSION,
    ICON_PATH,
    PROXY_IP_ADDR,
    PROXY_PORT,
    SUBSCRIPTION_PATH,
    TUN_CONFIG_PATH,
    TUN_LOG_PATH,
    TUN_PATH,
    USER_AGENT,
    XRAY_CONFIG_PATH,
    XRAY_CONFIGS_PATH,
    XRAY_LOG_PATH,
    XRAY_PATH,
)
from core.config import ConfigManager
from core.discord_proxy import DiscordProxyManager
from core.proxy import ProxyManager
from core.tun import TunManager
from core.xray import XrayManager
from ui.tray import Tray
from utils.i18n import get_current_language, tr
from utils.ipc import pass_to_main, start_server
from utils.update import get_latest_version, is_newer_version


class XrayGUI(QWidget):
    def __init__(self, server: QLocalServer) -> None:
        super().__init__()
        self.icon = QIcon(ICON_PATH)

        self.setWindowIcon(self.icon)
        self.setWindowTitle(APP_NAME)
        self.setFixedWidth(242 if get_current_language() == "ru" else 220)
        self.setFixedHeight(266)

        self.xray_manager = XrayManager(XRAY_PATH, XRAY_CONFIG_PATH, XRAY_LOG_PATH)
        self.config_manager = ConfigManager(
            USER_AGENT, SUBSCRIPTION_PATH, XRAY_CONFIGS_PATH, XRAY_CONFIG_PATH, TUN_CONFIG_PATH
        )
        self.tun_manager = TunManager(TUN_PATH, TUN_CONFIG_PATH, TUN_LOG_PATH)
        self.tun_enabled: bool = self.tun_manager.is_running()
        self.proxy_manager = ProxyManager(PROXY_IP_ADDR, PROXY_PORT)
        self.discord_proxy_manager = DiscordProxyManager()
        self.tray = Tray(self, self.icon)

        self._setup_ui()

        self._update_status_info()
        self._update_server_info()
        self._update_tun_info()
        self._update_system_proxy_info()
        self._update_discord_proxy_info()

        self._check_updates()

        server.newConnection.connect(self._on_ipc)

    def _setup_ui(self) -> None:
        status_layout = QHBoxLayout()
        self.status_label = QLabel()
        self.server_label = QLabel()
        status_layout.addWidget(self.status_label)
        status_layout.addStretch(1)
        status_layout.addWidget(self.server_label)

        buttons_layout = QVBoxLayout()
        buttons_layout.addLayout(status_layout)

        self.toggle_xray_button = QPushButton()
        self.toggle_xray_button.clicked.connect(self.toggle_xray)
        buttons_layout.addWidget(self.toggle_xray_button)

        self.select_server_button = QPushButton(tr("Select server"))
        self.select_server_button.clicked.connect(self.select_server)
        buttons_layout.addWidget(self.select_server_button)

        separator1 = QFrame()
        separator1.setFrameShape(QFrame.HLine)
        separator1.setFrameShadow(QFrame.Sunken)
        buttons_layout.addWidget(separator1)

        self.toggle_tun_button = QPushButton()
        self.toggle_tun_button.clicked.connect(self.toggle_tun)
        buttons_layout.addWidget(self.toggle_tun_button)

        self.toggle_system_proxy_button = QPushButton()
        self.toggle_system_proxy_button.clicked.connect(self.toggle_system_proxy)
        buttons_layout.addWidget(self.toggle_system_proxy_button)

        self.toggle_discord_proxy_button = QPushButton()
        self.toggle_discord_proxy_button.clicked.connect(self.toggle_discord_proxy)
        buttons_layout.addWidget(self.toggle_discord_proxy_button)

        separator2 = QFrame()
        separator2.setFrameShape(QFrame.HLine)
        separator2.setFrameShadow(QFrame.Sunken)
        buttons_layout.addWidget(separator2)

        import_subscription_button = QPushButton(tr("Import subscription"))
        import_subscription_button.clicked.connect(self.import_subscription)
        buttons_layout.addWidget(import_subscription_button)

        update_subscription_button = QPushButton(tr("Update subscription"))
        update_subscription_button.clicked.connect(self.update_subscription)
        buttons_layout.addWidget(update_subscription_button)

        self.setLayout(buttons_layout)

        self.tray.toggle_xray_action.triggered.connect(self.toggle_xray)
        self.tray.toggle_tun_action.triggered.connect(self.toggle_tun)
        self.tray.toggle_system_proxy_action.triggered.connect(self.toggle_system_proxy)
        self.tray.toggle_discord_proxy_action.triggered.connect(self.toggle_discord_proxy)

    def display_message(self, title: str, message: str) -> None:
        QMessageBox.information(self, title, message)

    def display_error(self, title: str, message: str) -> None:
        QMessageBox.critical(self, title, message)

    def _on_ipc(self) -> None:
        self.show()
        socket = self.sender().nextPendingConnection()
        if socket and socket.waitForReadyRead(50):
            try:
                args = json.loads(bytes(socket.readAll()).decode("utf-8"))
            except json.JSONDecodeError:
                args = []

            for arg in args:
                if arg.startswith("happ://add/"):
                    self.import_subscription(arg.removeprefix("happ://add/"))
        socket.close()

    def _update_status_info(self) -> None:
        running = self.xray_manager.is_running()
        self.status_label.setText(f"{tr('Status')}: {tr('Running') if running else tr('Stopped')}")
        self.toggle_xray_button.setText(f"{tr('Stop') if running else tr('Start')} VPN")
        self.tray.update_xray_action(running)

    def _update_server_info(self) -> None:
        current_server = self.config_manager.current_remark
        self.server_label.setText(f"{tr('Server')}: {tr('Not selected') if not current_server else current_server}")
        self.tray.update_server_menu(self.config_manager.xray_configs, current_server)

    def _update_tun_info(self) -> None:
        self.toggle_tun_button.setText(f"{tr('Disable') if self.tun_enabled else tr('Enable')} TUN")
        self.tray.update_tun_action(self.tun_enabled)

    def _update_system_proxy_info(self) -> None:
        enabled = self.proxy_manager.server_set()
        self.toggle_system_proxy_button.setText(f"{tr('Disable') if enabled else tr('Enable')} {tr('system proxy')}")
        self.tray.update_system_proxy_action(enabled)

    def _update_discord_proxy_info(self) -> None:
        enabled = self.discord_proxy_manager.is_enabled()
        self.toggle_discord_proxy_button.setText(f"{tr('Disable') if enabled else tr('Enable')} {tr('Discord proxy')}")
        self.tray.update_discord_proxy_action(enabled)

    def _check_updates(self) -> None:
        try:
            latest_version, download_url = get_latest_version()
            if latest_version and is_newer_version(APP_VERSION, latest_version):
                reply = QMessageBox.question(
                    self,
                    tr("Update available"),
                    tr(
                        "A new version {version} is available.\nWould you like to download it now?",
                        version=latest_version,
                    ),
                    QMessageBox.Yes | QMessageBox.No,
                )
                if reply == QMessageBox.Yes:
                    webbrowser.open(download_url)
        except Exception:
            pass

    def import_subscription(self, url: str | None = None) -> None:
        if not url:
            url, ok = QInputDialog.getText(self, tr("Import subscription"), tr("Enter subscription URL:"))
            if not ok or not url:
                return

        try:
            self.config_manager.import_configs(url)
        except Exception as e:
            self.display_error(tr("Error"), tr("Failed to import subscription:\n{error}", error=e))
            return

        self._update_server_info()
        self.display_message(tr("Success"), tr("Subscription imported successfully"))

    def update_subscription(self) -> None:
        if not self.config_manager.subscription_url:
            self.display_error(tr("Error"), tr("Import a subscription first"))
            return

        try:
            self.config_manager.import_configs(self.config_manager.subscription_url)
        except Exception as e:
            self.display_error(tr("Error"), tr("Failed to update subscription:\n{error}", error=e))
            return

        self._update_server_info()
        self.display_message(tr("Success"), tr("Subscription updated successfully"))

    def _select_server(self, remark: str) -> None:
        if not self.config_manager.select_config(remark):
            return

        self._update_server_info()
        if self.xray_manager.is_running():
            self.toggle_xray()
            self.toggle_xray()

    def select_server(self) -> None:
        if not self.config_manager.xray_configs:
            self.display_error(tr("Error"), tr("Import a subscription first"))
            return

        remarks = [server.get("remarks", "No remark") for server in self.config_manager.xray_configs]
        remark, ok = QInputDialog.getItem(self, tr("Select server"), tr("Choose a server:"), remarks, 0, False)
        if not ok or not remark:
            return

        self._select_server(remark)

    def toggle_xray(self) -> None:
        if self.xray_manager.is_running():
            self.xray_manager.stop()
            self.tun_manager.stop()
            self.proxy_manager.set_enable(False)
        else:
            if not self.config_manager.current_remark:
                self.display_error(tr("Error"), tr("Select a server first"))
                return

            if self.xray_manager.start():
                if self.proxy_manager.server_set():
                    self.proxy_manager.set_enable(True)
                if self.tun_enabled:
                    if not self.tun_manager.start():
                        self.tun_enabled = False
                        self.display_error(tr("Error"), tr("Failed to start TUN"))
            else:
                self.display_error(tr("Error"), tr("Failed to start VPN"))
                return

        self._update_status_info()
        self._update_system_proxy_info()
        self._update_tun_info()

    def toggle_system_proxy(self) -> None:
        if self.proxy_manager.server_set():
            self.proxy_manager.delete_server()
            self.proxy_manager.set_enable(False)
        else:
            self.proxy_manager.set_server()
            if self.xray_manager.is_running():
                self.proxy_manager.set_enable(True)

        self._update_system_proxy_info()

    def toggle_discord_proxy(self) -> None:
        if self.discord_proxy_manager.is_enabled():
            self.discord_proxy_manager.disable()
        else:
            if not self.discord_proxy_manager.enable():
                self.display_error(tr("Error"), tr("Failed to enable Discord proxy"))

        self._update_discord_proxy_info()

    def toggle_tun(self) -> None:
        if self.tun_enabled:
            self.tun_enabled = False
            self.tun_manager.stop()
        elif self.xray_manager.is_running():
            if not self.tun_manager.start():
                self.display_error(tr("Error"), tr("Failed to start TUN"))
            else:
                self.tun_enabled = True
        else:
            self.tun_enabled = True

        self._update_tun_info()

    def _quit(self) -> None:
        self.xray_manager.stop()
        self.proxy_manager.set_enable(False)
        self.tun_manager.stop()
        QApplication.quit()

    def showEvent(self, event: QEvent) -> None:
        super().showEvent(event)
        self.showNormal()
        self.activateWindow()
        self.tray.update_action_visibility()

    def hideEvent(self, event: QEvent) -> None:
        event.accept()
        self.tray.update_action_visibility()

    def closeEvent(self, event: QEvent) -> None:
        event.ignore()
        self.hide()
        self.tray.update_action_visibility()

    def changeEvent(self, event: QEvent) -> None:
        super().changeEvent(event)
        if event.type() == QEvent.WindowStateChange and self.isMinimized():
            event.ignore()
            self.hide()
            self.tray.update_action_visibility()


if __name__ == "__main__":
    if pass_to_main(sys.argv, APP_NAME):
        sys.exit(0)

    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)

    server = start_server(APP_NAME)
    window = XrayGUI(server)
    window.show()

    if len(sys.argv) > 1:
        arg = sys.argv[1]
        if arg.startswith("happ://add/"):
            window.import_subscription(arg.removeprefix("happ://add/"))

    sys.exit(app.exec())
