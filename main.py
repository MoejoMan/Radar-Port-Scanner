import sys
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.uic import loadUi
from portscan import PortScanner
from profiles import Profile_Manager
from PyQt5.QtCore import QObject, pyqtSignal, QThread

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        loadUi("Port_Scanner.ui", self)
        
        self.resize(1250, 800)
        self.scanner = PortScanner()
        self.profile_manager = Profile_Manager()
        
        # Signal connections
        self.StartScan_push.clicked.connect(self.start_scan)
    
    def start_scan(self):
        target = self.PortInput_line.text()
        if not target:
            self.Status_label.setText("Enter a target IP or hostname")
            return
        
        preset_text = self.PresetPorts_combo.currentText()
        if preset_text != "Preset Ports":
            port_input = preset_text.lower()
        else:
            port_input = self.CustomRange_line.text()
        
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
        print(result)
        self.Status_label.setText("Scan complete!")



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
