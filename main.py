import sys
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.uic import loadUi
from portscan import PortScanner
from profiles import Profile_Manager

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        loadUi("Port_Scanner.ui", self)
        
        self.resize(800, 600)
        self.scanner = PortScanner()
        self.profile_manager = Profile_Manager()
        
        # Signal connections
        self.StartScan_push.clicked.connect(self.start_scan)
    
    def start_scan(self):
        target = self.PortInput_line.text()
        if not target:
            self.Status_label.setText("Enter a target IP or hostname")
            return
        self.Status_label.setText(f"Scanning {target}...")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
