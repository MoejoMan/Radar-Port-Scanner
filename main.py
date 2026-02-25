import sys
import os
from pathlib import Path
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.uic import loadUi
from portscan import PortScanner
from profiles import Profile_Manager
from PyQt5.QtCore import QObject, pyqtSignal, QThread

# Get the directory where this script is located
APP_DIR = Path(__file__).resolve().parent


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        # Load UI from same directory as this script
        ui_file = APP_DIR / "Port_Scanner.ui"
        loadUi(str(ui_file), self)
        
        self.resize(1250, 800)
        self.scanner = PortScanner()
        self.profile_manager = Profile_Manager()
        self.thread = None
        self.worker = None
        
        # Signal connections
        self.StartScan_push.clicked.connect(self.start_scan)
        if hasattr(self, 'CancelScan_push'):
            self.CancelScan_push.clicked.connect(self.cancel_scan)
    
    def closeEvent(self, event):
        """Clean up resources on window close"""
        self.cancel_scan()
        self.profile_manager.close()
        event.accept()
    
    def start_scan(self):
        if self.thread and self.thread.isRunning():
            self.Status_label.setText("Scan already in progress")
            return
        
        target = self.PortInput_line.text().strip()
        if not target:
            self.Status_label.setText("Enter a target IP or hostname")
            return
        
        preset_text = self.PresetPorts_combo.currentText()
        if preset_text != "Preset Ports":
            port_input = preset_text.lower()
        else:
            port_input = self.CustomRange_line.text().strip()
        
        if not port_input:
            self.Status_label.setText("Select a preset or enter custom ports")
            return
        
        try:
            ports = self.scanner.parse_ports(port_input)
            if not ports:
                self.Status_label.setText("No valid ports found")
                return
        except Exception as e:
            self.Status_label.setText(f"Error parsing ports: {e}")
            return
        
        timeout = self.Timeout_spin.value() or 0.6
        threads = self.Threads_spin.value() or 200
        
        self.scanner.timeout = timeout
        self.scanner.threads = threads
        
        self.Status_label.setText(f"Scanning {target} ({len(ports)} ports)...")

        self.thread = QThread()
        self.worker = ScanWorker(target, ports, self.scanner)
        self.worker.moveToThread(self.thread)
        self.worker.progress.connect(self.update_progress)
        
        self.progressBar.setMaximum(len(ports))
        self.progressBar.setValue(0)

        self.worker.finished.connect(self.scan_finished)

        self.tableWidget.setRowCount(0)  # Clear previous results
        self.tableWidget.setColumnCount(4)
        self.tableWidget.setHorizontalHeaderLabels(["Port", "Status", "Service", "Banner"])

        self.thread.started.connect(self.worker.run)
        self.thread.start()

    def update_progress(self, scanned, total):
        self.progressBar.setMaximum(total)
        self.progressBar.setValue(scanned)

    def scan_finished(self, result):
        # Clean up thread
        if self.thread:
            self.thread.quit()
            self.thread.wait()
            self.thread = None
        
        if result.get("success"):
            self.display_results(result.get("results", {}))
            self.Status_label.setText("Scan complete!")
        else:
            self.Status_label.setText(f"Scan failed: {result.get('error', 'Unknown error')}")
    
    def cancel_scan(self):
        if self.thread and self.thread.isRunning():
            self.thread.quit()
            self.thread.wait()
            self.Status_label.setText("Scan cancelled")
    
    def display_results(self, results):
        """Display scan results in table widget"""
        from PyQt5.QtWidgets import QTableWidgetItem
        open_ports = results.get("open_ports", [])
        self.tableWidget.setRowCount(len(open_ports))
        
        for row, port_info in enumerate(open_ports):
            port = str(port_info.get("port", ""))
            status = port_info.get("status", "unknown")
            service = self.scanner.get_service_name(int(port)) if port else ""
            banner = port_info.get("banner", "")
            
            # Truncate banner if too long
            if banner and len(banner) > 50:
                banner = banner[:47] + "..."
            
            self.tableWidget.setItem(row, 0, QTableWidgetItem(port))
            self.tableWidget.setItem(row, 1, QTableWidgetItem(status))
            self.tableWidget.setItem(row, 2, QTableWidgetItem(service))
            self.tableWidget.setItem(row, 3, QTableWidgetItem(banner or "N/A"))



class ScanWorker(QObject):
    def __init__(self, target, ports, scanner):
        super().__init__()
        self.target = target
        self.ports = ports
        self.scanner = scanner

        self.progress = pyqtSignal(int, int)
        self.finished = pyqtSignal(dict)

    def run(self):
        # Define nested progress callback
        def on_progress(scanned, total):
            self.progress.emit(scanned, total)
        
        # Set callback and run scan
        self.scanner.set_progress_callback(on_progress)
        result = self.scanner.scan(self.target, self.ports)
        self.finished.emit(result)
        

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
