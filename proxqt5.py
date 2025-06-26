#!/usr/bin/python3

from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QListWidget,
    QPushButton,
    QMessageBox,
)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QTimer
from PyQt5.QtCore import Qt

from proxmoxer import ProxmoxAPI
import subprocess
import pathlib
import urllib3
import sys

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class ProxmoxVMManager(QWidget):
    def __init__(self):
        super().__init__()
        self.prox = ProxmoxAPI(
            "<your-proxmox-host>",
            user="<your-api-user>@pam",
            token_name="<your-token-name>",
            token_value="<your-token-secret>",
            verify_ssl=False,
        )
        self.vm_list = []
        self.init_ui()
        self.refresh_timer = QTimer(self)
        self.refresh_timer.timeout.connect(self.refresh_vm_list)
        self.refresh_timer.start(3000)  # Refresh every 3 seconds
        self.refresh_vm_list()

    def init_ui(self):
        self.setWindowTitle("Proxmox VM Manager")
        icon_path = str(pathlib.Path(__file__).parent / "proxmox.png")
        self.setWindowIcon(QIcon(icon_path))

        # Layouts
        main_layout = QHBoxLayout()
        button_layout = QVBoxLayout()

        # VM List
        self.list_widget = QListWidget(self)
        main_layout.addWidget(self.list_widget)

        # Buttons
        self.remote_button = QPushButton("Remote")
        self.remote_button.clicked.connect(self.remote_vm)
        button_layout.addWidget(self.remote_button)

        self.power_on_button = QPushButton("Power On")
        self.power_on_button.clicked.connect(self.power_on_vm)
        button_layout.addWidget(self.power_on_button)

        self.power_off_button = QPushButton("Power Off")
        self.power_off_button.clicked.connect(self.power_off_vm)
        button_layout.addWidget(self.power_off_button)

        self.refresh_button = QPushButton("Refresh")
        self.refresh_button.clicked.connect(self.refresh_vm_list)
        button_layout.addWidget(self.refresh_button)

        self.exit_button = QPushButton("Exit")
        self.exit_button.clicked.connect(self.close)
        button_layout.addWidget(self.exit_button)

        main_layout.addLayout(button_layout)
        self.setLayout(main_layout)

        self.setFixedSize(500, 400)

    def refresh_vm_list(self):
        # Save the currently selected item's text
        current_selection = self.list_widget.currentItem().text() if self.list_widget.currentItem() else None

        # Clear and repopulate the VM list
        self.vm_list.clear()
        self.list_widget.clear()
        for node in self.prox.nodes.get():
            for vm in self.prox.nodes(node["node"]).qemu.get():
                vm_info = f'{vm["vmid"]} | {vm["name"]} ({vm["status"]})'
                self.vm_list.append((vm["vmid"], node["node"], vm["status"]))
                self.list_widget.addItem(vm_info)

        # Sort items numerically
        items = [self.list_widget.item(i).text() for i in range(self.list_widget.count())]
        sorted_items = sorted(items, key=lambda x: int(x.split()[0]))
        self.list_widget.clear()
        self.list_widget.addItems(sorted_items)

        # Restore the selection if possible
        if current_selection:
            matching_items = self.list_widget.findItems(current_selection, Qt.MatchExactly)
            if matching_items:
                self.list_widget.setCurrentItem(matching_items[0])

    def get_selected_vm(self):
        selected_items = self.list_widget.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Warning", "No VM selected.")
            return None
        selected_text = selected_items[0].text()
        vmid = int(selected_text.split("|")[0].strip())
        return next((vm for vm in self.vm_list if vm[0] == vmid), None)

    def remote_vm(self):
        vm = self.get_selected_vm()
        if not vm:
            return
        vmid, node, status = vm
        if status == "stopped":
            reply = QMessageBox.question(
                self,
                "Remote Console",
                "Selected VM is not online, start it?",
                QMessageBox.Yes | QMessageBox.No,
            )
            if reply == QMessageBox.Yes:
                self.prox.nodes(node).qemu(vmid).status.post("start")
                subprocess.run(["sudo", "remotepv", str(vmid)]) #Add the path to remotepv otherwise this may fail to start
        elif status == "running":
            subprocess.run(["sudo", "remotepv", str(vmid)]) #Add the path to remotepv otherwise this may fail to start
        self.refresh_vm_list()

    def power_on_vm(self):
        vm = self.get_selected_vm()
        if not vm:
            return
        vmid, node, _ = vm
        self.prox.nodes(node).qemu(vmid).status.post("start")
        self.refresh_vm_list()

    def power_off_vm(self):
        vm = self.get_selected_vm()
        if not vm:
            return
        vmid, node, _ = vm
        self.prox.nodes(node).qemu(vmid).status.post("shutdown")
        self.refresh_vm_list()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ProxmoxVMManager()
    window.show()
    sys.exit(app.exec_())
