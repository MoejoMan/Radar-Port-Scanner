import sys
import os
from pathlib import Path
from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidgetItem
from PyQt5.QtGui import QColor
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
            print(f"[DEBUG] Parsed ports: {ports}")
        except Exception as e:
            error = f"Error parsing ports: {e}"
            self.Status_label.setText(error)
            print(f"[ERROR] {error}")
            return
        
        timeout = float(self.Timeout_spin.value()) or 0.6
        threads = int(self.Threads_spin.value()) or 200
        
        self.scanner.timeout = timeout
        self.scanner.threads = threads
        
        print(f"[DEBUG] Scan starting: target={target}, ports={len(ports)}, timeout={timeout}, threads={threads}")
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
        # Print every 10% for debugging
        if scanned % max(1, total // 10) == 0 or scanned == total:
            print(f"[DEBUG] Progress: {scanned}/{total} ({100*scanned//total}%)")

    def scan_finished(self, result):
        # Clean up thread
        if self.thread:
            self.thread.quit()
            self.thread.wait()
            self.thread = None
        
        print(f"[DEBUG] Scan finished with result: {result}")
        
        if result.get("success"):
            scan_results = result.get("results", {})
            print(f"[DEBUG] Display results called with: {scan_results}")
            self.display_results(scan_results)
            
            # Show detailed summary
            summary = scan_results.get("summary", {})
            duration = scan_results.get("duration_s", 0)
            target = scan_results.get("target", "Unknown")
            status_msg = f"Scan complete! {target}: {summary.get('total_open', 0)} open, {summary.get('total_closed', 0)} closed, {summary.get('total_filtered', 0)} filtered ({duration:.2f}s)"
            self.Status_label.setText(status_msg)
        else:
            error_msg = f"Scan failed: {result.get('error', 'Unknown error')}"
            self.Status_label.setText(error_msg)
            print(f"[ERROR] {error_msg}")
    
    def cancel_scan(self):
        if self.thread and self.thread.isRunning():
            self.thread.quit()
            self.thread.wait()
            self.Status_label.setText("Scan cancelled")
    
    def display_results(self, results):
        """Display scan results in table widget"""
        open_ports = results.get("open_ports", [])
        closed_ports = results.get("closed_ports", [])
        filtered_ports = results.get("filtered_ports", [])
        
        print(f"[DEBUG] display_results called with {len(open_ports)} open, {len(closed_ports)} closed, {len(filtered_ports)} filtered ports")
        
        # Set table row count to total scanned ports
        total_ports = len(open_ports) + len(closed_ports) + len(filtered_ports)
        self.tableWidget.setRowCount(total_ports)
        
        row = 0
        
        # Display open ports first (with green highlight)
        for port_info in open_ports:
            port = str(port_info.get("port", ""))
            status = port_info.get("status", "unknown")
            service = self.scanner.get_service_name(int(port)) if port else ""
            banner = port_info.get("banner", "")
            
            # Truncate banner if too long
            if banner and len(banner) > 50:
                banner = banner[:47] + "..."
            
            port_item = QTableWidgetItem(port)
            port_item.setBackground(QColor(76, 175, 80))  # Green for open
            
            self.tableWidget.setItem(row, 0, port_item)
            self.tableWidget.setItem(row, 1, QTableWidgetItem(status))
            self.tableWidget.setItem(row, 2, QTableWidgetItem(service))
            self.tableWidget.setItem(row, 3, QTableWidgetItem(banner or "N/A"))
            row += 1
        
        # Display closed ports with gray highlight
        for port_info in closed_ports:
            port = str(port_info.get("port", ""))
            status = port_info.get("status", "closed")
            service = self.scanner.get_service_name(int(port)) if port else ""
            
            port_item = QTableWidgetItem(port)
            port_item.setBackground(QColor(158, 158, 158))  # Gray for closed
            
            self.tableWidget.setItem(row, 0, port_item)
            self.tableWidget.setItem(row, 1, QTableWidgetItem(status))
            self.tableWidget.setItem(row, 2, QTableWidgetItem(service))
            self.tableWidget.setItem(row, 3, QTableWidgetItem("N/A"))
            row += 1
        
        # Display filtered ports
        for port_info in filtered_ports:
            port = str(port_info.get("port", ""))
            status = port_info.get("status", "filtered")
            service = self.scanner.get_service_name(int(port)) if port else ""
            
            port_item = QTableWidgetItem(port)
            port_item.setBackground(QColor(255, 193, 7))  # Yellow for filtered
            
            self.tableWidget.setItem(row, 0, port_item)
            self.tableWidget.setItem(row, 1, QTableWidgetItem(status))
            self.tableWidget.setItem(row, 2, QTableWidgetItem(service))
            self.tableWidget.setItem(row, 3, QTableWidgetItem("N/A"))
            row += 1
        
        print(f"[DEBUG] Table updated with {row} total rows")



class ScanWorker(QObject):
    progress = pyqtSignal(int, int)
    finished = pyqtSignal(dict)
    
    def __init__(self, target, ports, scanner):
        super().__init__()
        self.target = target
        self.ports = ports
        self.scanner = scanner

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
