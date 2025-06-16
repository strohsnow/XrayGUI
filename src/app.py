import json
import sys

from PySide6.QtCore import QEvent
from PySide6.QtGui import QIcon
from PySide6.QtNetwork import QLocalServer
from PySide6.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QInputDialog,
    QLabel,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from config import (
    CONFIG_PATH,
    CONFIGS_PATH,
    ICON_PATH,
    PROXY_IP_ADDR,
    PROXY_PORT,
    SOCKET_NAME,
    SUB_PATH,
    USER_AGENT,
    XRAY_PATH,
)
from core.proxy import ProxyManager
from core.server import ServerManager
from core.xray import XrayManager
from ui.tray import Tray
from utils.ipc import pass_to_main, start_server


class XrayGUI(QWidget):
    def __init__(self, server: QLocalServer) -> None:
        super().__init__()
        self.icon = QIcon(ICON_PATH)

        self.setWindowIcon(self.icon)
        self.setWindowTitle("XrayGUI")
        self.setFixedSize(220, 188)

        self.xray_manager = XrayManager(XRAY_PATH, CONFIG_PATH)
        self.server_manager = ServerManager(USER_AGENT, SUB_PATH, CONFIGS_PATH, CONFIG_PATH)
        self.proxy_manager = ProxyManager(PROXY_IP_ADDR, PROXY_PORT)
        self.tray = Tray(self, self.icon)

        self._setup_ui()

        self._update_status_info()
        self._update_server_info()
        self._update_system_proxy_info()

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

        self.select_server_button = QPushButton("Select Server")
        self.select_server_button.clicked.connect(self.select_server)
        buttons_layout.addWidget(self.select_server_button)

        self.toggle_system_proxy_button = QPushButton()
        self.toggle_system_proxy_button.clicked.connect(self.toggle_system_proxy)
        buttons_layout.addWidget(self.toggle_system_proxy_button)

        import_subscription_button = QPushButton("Import Subscription")
        import_subscription_button.clicked.connect(self.import_subscription)
        buttons_layout.addWidget(import_subscription_button)

        update_subscription_button = QPushButton("Update Subscription")
        update_subscription_button.clicked.connect(self.update_subscription)
        buttons_layout.addWidget(update_subscription_button)

        self.setLayout(buttons_layout)

        self.tray.toggle_xray_action.triggered.connect(self.toggle_xray)
        self.tray.toggle_system_proxy_action.triggered.connect(self.toggle_system_proxy)

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
        self.status_label.setText(f"Status: {'Running' if running else 'Stopped'}")
        self.toggle_xray_button.setText(f"{'Stop' if running else 'Start'} Xray")
        self.tray.update_xray_action(running)

    def _update_server_info(self) -> None:
        current_server = self.server_manager.current_server
        self.server_label.setText(f"Server: {'Not Selected' if not current_server else current_server}")
        self.tray.update_server_menu(self.server_manager.servers, current_server)

    def _update_system_proxy_info(self) -> None:
        enabled = self.proxy_manager.server_set()
        self.toggle_system_proxy_button.setText(f"{'Disable' if enabled else 'Enable'} System Proxy")
        self.tray.update_system_proxy_action(enabled)

    def import_subscription(self, url: str | None = None) -> None:
        if not url:
            url, ok = QInputDialog.getText(self, "Import subscription", "Enter subscription URL:")
            if not ok or not url:
                return

        try:
            self.server_manager.import_subscription(url)
        except Exception as e:
            self.display_error("Error", f"Failed to import subscription:\n{e}")
            return

        self._update_server_info()
        self.display_message("Success", "Subscription imported successfully")

    def update_subscription(self) -> None:
        if not self.server_manager.subscription_url:
            self.display_error("Error", "Please import a subscription first")
            return

        try:
            self.server_manager.import_subscription(self.server_manager.subscription_url)
        except Exception as e:
            self.display_error("Error", f"Failed to update subscription:\n{e}")
            return

        self._update_server_info()
        self.display_message("Success", "Subscription updated successfully")

    def _select_server(self, remark: str) -> None:
        if not self.server_manager.select_server(remark):
            return

        self._update_server_info()
        if self.xray_manager.is_running():
            self.toggle_xray()
            self.toggle_xray()

    def select_server(self) -> None:
        if not self.server_manager.servers:
            self.display_error("Error", "Please import a subscription first")
            return

        remarks = [server.get("remarks", "No remark") for server in self.server_manager.servers]
        remark, ok = QInputDialog.getItem(self, "Select server", "Choose a server:", remarks, 0, False)
        if not ok or not remark:
            return

        self._select_server(remark)

    def toggle_xray(self) -> None:
        if self.xray_manager.is_running():
            self.xray_manager.stop()
            self.proxy_manager.set_enable(False)
        else:
            if not self.server_manager.current_server:
                self.display_error("Error", "Please select a server first")
                return

            if self.xray_manager.start():
                if self.proxy_manager.server_set():
                    self.proxy_manager.set_enable(True)
            else:
                self.display_error("Error", "Failed to start Xray")
                return

        self._update_status_info()
        self._update_system_proxy_info()

    def toggle_system_proxy(self) -> None:
        if self.proxy_manager.server_set():
            self.proxy_manager.delete_server()
            self.proxy_manager.set_enable(False)
        else:
            self.proxy_manager.set_server()
            if self.xray_manager.is_running():
                self.proxy_manager.set_enable(True)

        self._update_system_proxy_info()

    def _quit(self) -> None:
        self.xray_manager.stop()
        self.proxy_manager.set_enable(False)
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
        self.tray.show_message("XrayGUI", "XrayGUI is running in the system tray")
        self.tray.update_action_visibility()

    def changeEvent(self, event: QEvent) -> None:
        super().changeEvent(event)
        if event.type() == QEvent.WindowStateChange and self.isMinimized():
            event.ignore()
            self.hide()
            self.tray.show_message("XrayGUI", "XrayGUI is running in the system tray")
            self.tray.update_action_visibility()


if __name__ == "__main__":
    if pass_to_main(sys.argv, SOCKET_NAME):
        sys.exit(0)

    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)

    server = start_server(SOCKET_NAME)
    window = XrayGUI(server)
    window.show()

    if len(sys.argv) > 1:
        arg = sys.argv[1]
        if arg.startswith("happ://add/"):
            window.import_subscription(arg.removeprefix("happ://add/"))

    sys.exit(app.exec())
