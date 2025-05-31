import json
import os
import sys

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

import config
import firewall
import nssm
import subscription
import winproxy


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("XrayGUI")
        self.setFixedSize(220, 150)

        self.remark: str | None = None
        self.proxy = winproxy.WinProxy(config.PROXY_IP_ADDR, config.PROXY_PORT)

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

        self.toggle_system_proxy_button = QPushButton()
        self.toggle_system_proxy_button.clicked.connect(self.toggle_system_proxy)
        buttons_layout.addWidget(self.toggle_system_proxy_button)

        self.import_subscription_button = QPushButton("Import subscription")
        self.import_subscription_button.clicked.connect(self.import_subscription)
        buttons_layout.addWidget(self.import_subscription_button)

        self.update_subscription_button = QPushButton("Update subscription")
        self.update_subscription_button.clicked.connect(self.update_subscription)
        buttons_layout.addWidget(self.update_subscription_button)

        self.setLayout(buttons_layout)
        self.refresh_status_display()
        self.refresh_proxy_display()

    def display_message(self, title: str, message: str) -> None:
        QMessageBox.information(self, title, message)

    def display_error(self, title: str, message: str) -> None:
        QMessageBox.critical(self, title, message)

    def refresh_status_display(self) -> None:
        if self.xray_enabled():
            self.status_label.setText("Status: Running")
            if self.remark is None and os.path.isfile(config.CONFIG_JSON):
                with open(config.CONFIG_JSON, "r", encoding="utf-8") as f:
                    cfg = json.load(f)
                self.remark = cfg.get("remarks", "")
            self.server_label.setText(f"Server: {self.remark or 'Not selected'}")
            self.toggle_xray_button.setText("Stop Xray")
        else:
            self.status_label.setText("Status: Stopped")
            self.server_label.setText("Server: Not selected")
            self.toggle_xray_button.setText("Start Xray")

    def refresh_proxy_display(self) -> None:
        if self.proxy.server_set():
            self.toggle_system_proxy_button.setText("Disable system proxy")
        else:
            self.toggle_system_proxy_button.setText("Enable system proxy")

    def import_subscription(self) -> None:
        url, ok = QInputDialog.getText(
            self, "Import subscription", "Enter subscription URL:"
        )
        if not ok or not url:
            self.display_error("Error", "Invalid subscription URL")
            return

        if not os.path.exists(config.CONFIG_DIR):
            os.makedirs(config.CONFIG_DIR)

        try:
            subscription.get_config_json(url, config.CONFIGS_JSON)
            self.display_message("Success", "Subscription imported successfully")
        except Exception as e:
            self.display_error("Error", f"Failed to import subscription:\n{e}")

        with open(config.SUB_TXT, "w", encoding="utf-8") as f:
            f.write(url.strip())

    def update_subscription(self) -> None:
        if not os.path.isfile(config.SUB_TXT):
            self.display_error("Error", "Please import a subscription first")
            return

        with open(config.SUB_TXT, "r", encoding="utf-8") as f:
            url = f.read().strip()

        try:
            subscription.get_config_json(url, config.CONFIGS_JSON)
            self.display_message("Success", "Subscription updated successfully")
        except Exception as e:
            self.display_error("Error", f"Failed to update subscription:\n{e}")

    def choose_subscription(self) -> dict | None:
        if not os.path.isfile(config.CONFIGS_JSON):
            self.display_error("Error", "Please import a subscription first")
            return None

        with open(config.CONFIGS_JSON, "r", encoding="utf-8") as f:
            configs = json.load(f)

        remarks = [entry["remarks"] for entry in configs]
        if not remarks:
            self.display_error("Error", "Server list is empty")
            return None

        item, ok = QInputDialog.getItem(
            self, "Select server", "Choose a server:", remarks, 0, False
        )
        if not ok:
            return None

        self.server_label.setText(f"Server: {item}")
        self.remark = item
        return configs[remarks.index(item)]

    def toggle_xray(self) -> None:
        if self.xray_enabled():
            self.stop_xray()
        else:
            self.start_xray()

    def start_xray(self) -> None:
        sub = self.choose_subscription()
        if not sub:
            self.display_error("Error", "Server is not selected")
            return

        with open(config.CONFIG_JSON, "w", encoding="utf-8") as f:
            json.dump(sub, f, ensure_ascii=False, indent=2)

        try:
            firewall.add_rule(config.FIREWALL_RULE, config.XRAY_EXE)
            nssm.install_service(
                config.NSSM_EXE,
                config.XRAY_SERVICE,
                config.XRAY_EXE,
                ["-c", config.CONFIG_JSON],
            )
            nssm.start_service(config.NSSM_EXE, config.XRAY_SERVICE)
        except Exception as e:
            self.display_error("Error", f"Failed to start VPN:\n{e}")

        if self.proxy.server_set():
            self.proxy.set_enable(True)

        self.refresh_status_display()

    def stop_xray(self) -> None:
        try:
            nssm.stop_service(config.NSSM_EXE, config.XRAY_SERVICE)
            nssm.remove_service(config.NSSM_EXE, config.XRAY_SERVICE)
            firewall.delete_rule(config.FIREWALL_RULE)
        except Exception as e:
            self.display_error("Error", f"Failed to stop VPN:\n{e}")

        self.proxy.set_enable(False)

        self.refresh_status_display()

    def xray_enabled(self) -> bool:
        try:
            return nssm.service_running(config.NSSM_EXE, config.XRAY_SERVICE)
        except FileNotFoundError as e:
            self.display_error("Error", f"{e}")
            sys.exit(1)

    def toggle_system_proxy(self) -> None:
        if self.proxy.server_set():
            self.proxy.delete_server()
            self.proxy.set_enable(False)
        else:
            self.proxy.set_server()
            if self.xray_enabled():
                self.proxy.set_enable(True)

        self.refresh_proxy_display()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
