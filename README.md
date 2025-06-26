# Proxmox Remote VM Connector for macOS

This project provides a pair of tools to simplify remote SPICE-based VM access to your Proxmox (PVE) environment from macOS, with support for USB redirection and optional GUI controls.

## 🔧 Components

- `remotepv`: A Bash script that queries the Proxmox API for the correct node and VM information, then launches `remote-viewer` with custom USB filter settings.
- `proxqt5.py`: A PyQt5-based GUI that lists all VMs, lets you power them on/off, and connect via `remotepv`.
- `proxmox.png`: An icon for the application.  Replace this if required.

These tools are designed to be used together. The GUI handles VM selection and power management, while `remotepv` handles the low-level SPICE session connection.
I recommend you use a venv.  If you do this, change the python3 location at the top of proxqt5.py

---

## 🖥️ Requirements

- macOS (tested on recent versions)
- `remote-viewer` installed (`brew install remote-viewer`)
- `jq` and `curl` installed
- python requires PyQT5, proxmoxer and urllib3 (`pip install -r requirements.txt`)
- A Proxmox API token (see below)
- Proxmox node accessible over network

---

## 🔐 Setup

1. Create an API token in Proxmox:
   - Go to your user (`username@pam` or similar)
   - Create a token with `VM.Console`, `VM.PowerMgmt`, and `VM.Audit` permissions
   - Copy the token *secret* when shown

2. Edit the `remotepv` script:
   - Replace the `TOKEN`, `SECRET`, and `HOST` values with your own
   - Optionally adjust USB filters

3. Make it executable:

```bash
chmod +x remotepv
```

---

## 🚀 Usage

To launch a remote VM session directly:

```bash
sudo ./remotepv <vmid>
```

To use the GUI (must also have sudo rights to invoke the script):

```bash
python3 proxqt5.py
```

From the GUI, you can:
- View all QEMU VMs
- Power on/off VMs
- Connect to a selected VM using `remotepv`

---

## ⚠️ Notes

- USB redirection may require permissions and/or filtering. Adjust the `usb-filter` string in `remotepv` if needed.
- SPICE proxy mode is used; `remote-viewer` must be installed and in your PATH.
- Ensure the VM has the QEMU display set to SPICE.

---

MIT licensed. Contributions welcome.
