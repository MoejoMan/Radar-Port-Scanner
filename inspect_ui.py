from PyQt5 import QtWidgets, uic
import sys

app = QtWidgets.QApplication(sys.argv)
win = QtWidgets.QMainWindow()
uic.loadUi("Port_Scanner.ui", win)

print("Widgets in UI:")
for w in win.findChildren(QtWidgets.QWidget):
    print(f"{type(w).__name__}: {w.objectName()}")

# Keep window closed; just enumerate
sys.exit(0)