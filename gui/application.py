import logging
import sys
import typing

import importlib.resources

from PyQt5.QtCore import (
    Qt, QRegExp, pyqtSignal, pyqtSlot
)
from PyQt5.QtGui import (
    QIcon, QPalette, QColor, QRegExpValidator
)
from PyQt5.QtWidgets import (
    QAction, QApplication, QDesktopWidget, QDialog, QFileDialog, QStackedWidget, 
    QHBoxLayout, QVBoxLayout, QGridLayout, QFormLayout, QLabel, QMainWindow, QToolBar,
    QWidget, QComboBox, QLineEdit, QCheckBox, QPushButton, QMessageBox
)

from printer import (
    PRINTER_TYPES, SERIAL_BYTESIZES, SERIAL_PARITIES, SERIAL_STOPBITS,
    PrinterBuilder, Printer
)

from gui.rightbar import RightBar
from gui.tabs import Tabs


logger = logging.getLogger(__name__)


class Resources(object):
    """ Resources importlib loader """
    def __init__(self) -> None:
        logger.info("Resources - start")

        ref = importlib.resources.files('gui.images') / 'favicon.ico'
        with importlib.resources.as_file(ref) as fav:
            self.favicon = QIcon(str(fav.absolute()))
        
        logger.info("Resources - loaded")


class MainApp(QApplication):
    """ QApplication with styling. """

    def __init__(self, argv: typing.List[str]) -> None:
        super(MainApp, self).__init__(argv)
        self.set_style()

    def set_style(self) -> None:
        self.setStyle("Fusion")
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(53, 53, 53))
        palette.setColor(QPalette.WindowText, Qt.white)
        palette.setColor(QPalette.Base, QColor(25, 25, 25))
        palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
        palette.setColor(QPalette.ToolTipBase, Qt.white)
        palette.setColor(QPalette.ToolTipText, Qt.white)
        palette.setColor(QPalette.Text, Qt.white)
        palette.setColor(QPalette.Button, QColor(53, 53, 53))
        palette.setColor(QPalette.ButtonText, Qt.white)
        palette.setColor(QPalette.BrightText, Qt.red)
        palette.setColor(QPalette.Link, QColor(42, 130, 218))
        palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
        palette.setColor(QPalette.HighlightedText, Qt.black)
        self.setPalette(palette)


class MainWindow(QMainWindow):
    """ QMainWindow wraps all of the widgets for the application. """

    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)

        self.res = Resources()
        self.driver = None

        self.configDialog = ConfigDialog()
        self.configDialog.signalConfigured.connect(lambda driver: self.config_dialog_slot(driver))
        self.configDialog.exec_()

        if self.driver is not None:
            self.printer = Printer(self.driver)
            logger.info(f"Printer has loaded with driver {self.driver}")
        else:
            logger.error("No valid driver was provided, exiting...")
            QApplication.quit()
            sys.exit()

        self.resize(1024, 768)
        self.setWindowTitle(f'pyqt-escpos')
        self.setWindowIcon(self.res.favicon)
        
        self.widget = QWidget()
        self.setCentralWidget(self.widget)

        layout = QGridLayout()

        self.bar = RightBar(self.printer, parent=self.widget)
        self.tabs = Tabs(self.printer, self.bar.add_to_queue, parent=self.widget)

        layout.addWidget(self.tabs, 0, 0)
        layout.addWidget(self.bar, 0, 1)
        layout.setColumnStretch(0, 2)
        layout.setColumnStretch(1, 1)
        self.widget.setLayout(layout)
        
        self.status = self.statusBar()
        self.status.showMessage(f"Ready with {self.driver}", 3000)

    @pyqtSlot()
    def config_dialog_slot(self, driver):
        self.driver = driver
        # logger.debug(f"{self.driver} {type(self.driver)}")

    def open_file(self):
        """Open a QFileDialog to allow the user to open a file into the application."""
        filename, accepted = QFileDialog.getOpenFileName(self, 'Open File')

        if accepted:
            with open(filename) as file:
                file.read()


class ConfigDialog(QDialog):
    """ QDialog with query parameters for printer connection """
    signalConfigured = pyqtSignal(object)

    def __init__(self, parent=None) -> None:
        super(ConfigDialog, self).__init__(parent)

        self.printer = PrinterBuilder()
        self.res = Resources()

        self.setWindowTitle('Config')
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self.setWindowIcon(self.res.favicon)

        lblConnection = QLabel('Connection:')
        cmbConnection = QComboBox()
        cmbConnection.addItems(PRINTER_TYPES)
        cmbConnection.currentIndexChanged.connect(self.display)

        self.pagesStack = QStackedWidget(self)
        self.pagesStack.addWidget(self.build_usb_page())
        self.pagesStack.addWidget(self.build_network_page())
        self.pagesStack.addWidget(self.build_serial_page())
        self.pagesStack.addWidget(self.build_file_page())

        btnConnect = QPushButton("Connect")
        btnConnect.clicked.connect(self.connect)

        self.layout = QVBoxLayout()
        self.layout.setAlignment(Qt.AlignVCenter)

        self.layout.addWidget(lblConnection)
        self.layout.addWidget(cmbConnection)
        self.layout.addWidget(self.pagesStack)
        self.layout.addWidget(btnConnect)
        self.setLayout(self.layout)

        self.resize(300, 300)
        self.setFixedSize(self.size())

    def connect(self) -> None:
        conn = PRINTER_TYPES[self.pagesStack.currentIndex()]

        callables = self.pagesStack.currentWidget().params
        kwargs = {}
        for k,v in callables.items():
            kwargs[k] = v() # convert functions to return values by calling them

        logger.info(f"Trying to connect with type {conn} and kwargs {kwargs.items()}")
        isSuccess = self.printer.build(conn, **kwargs)
        if isSuccess == True:
            logger.info("Connection success, configuration complete.")
            self.signalConfigured.emit(self.printer.get())
            self.accept() # closing window
        else:
            self.show_alert(f"Failed to connect with {conn}! Double check you configuration!")

    def show_alert(self, msg: str) -> None:
        mb = QMessageBox()
        mb.setIcon(QMessageBox.Icon.Critical)
        mb.setWindowTitle("Alert")
        mb.setText(f"{msg}")
        mb.setStandardButtons(QMessageBox.Ok)
        mb.exec_()

    def display(self, idx: int) -> None:
        self.pagesStack.setCurrentIndex(idx)

    def build_usb_page(self) -> QWidget:
        widget = QWidget()
        layout = QFormLayout()

        usbValidator = QRegExpValidator(QRegExp("0x[0-9A-Fa-f]{4}"))
        timeoutValidator = QRegExpValidator(QRegExp("[0-9]+"))

        vid = QLineEdit("0x28E9")
        vid.setValidator(usbValidator)
        layout.addRow("VID", vid)

        pid = QLineEdit("0x0289")
        pid.setValidator(usbValidator)
        layout.addRow("PID", pid)

        timeout = QLineEdit("0")
        timeout.setValidator(timeoutValidator)
        layout.addRow("Timeout", timeout)

        widget.setLayout(layout)
        widget.params = {"vid" : vid.text, "pid" : pid.text, "timeout" : timeout.text }
        return widget

    def build_network_page(self) -> QWidget:  
        widget = QWidget() 
        layout = QFormLayout() 

        ipValidator = QRegExpValidator(QRegExp("^((25[0-5]|(2[0-4]|1\d|[1-9]|)\d)(\.(?!$)|$)){4}$"))
        decimalValidator = QRegExpValidator(QRegExp("[0-9]+"))

        host = QLineEdit("192.168.1.100")
        host.setValidator(ipValidator)
        layout.addRow("Host", host)

        port = QLineEdit("9100")
        port.setValidator(decimalValidator)
        layout.addRow("Port", port)

        timeout = QLineEdit("60")
        timeout.setValidator(decimalValidator)
        layout.addRow("Timeout", timeout)

        widget.setLayout(layout)
        widget.params = {"host" : host.text, "port" : port.text, "timeout" : timeout.text }
        return widget

    def build_serial_page(self) -> QWidget:
        widget = QWidget()
        layout = QFormLayout() 

        decimalValidator = QRegExpValidator(QRegExp("[0-9]+"))

        port = QLineEdit("/dev/ttyS0")
        layout.addRow("Serial", port)

        baudrate = QLineEdit("9600")
        baudrate.setValidator(decimalValidator)
        layout.addRow("Baudrate", baudrate)

        timeout = QLineEdit("1")
        timeout.setValidator(decimalValidator)
        layout.addRow("Timeout", timeout)

        bytesize = QComboBox()
        bytesize.addItems(map(str, SERIAL_BYTESIZES))
        bytesize.setCurrentIndex(SERIAL_BYTESIZES.index(8))
        layout.addRow("Bytesize", bytesize)

        parity = QComboBox()
        parity.addItems(SERIAL_PARITIES)
        bytesize.setCurrentIndex(SERIAL_PARITIES.index("N"))
        layout.addRow("Parity", parity)

        stopbits = QComboBox()
        stopbits.addItems(map(str, SERIAL_STOPBITS))
        bytesize.setCurrentIndex(SERIAL_STOPBITS.index(1))
        layout.addRow("Stopbits", stopbits)

        xonoff = QCheckBox()
        dsrdtr = QCheckBox()
        dsrdtr.setChecked(True)
        layout.addRow("XON/XOFF", xonoff)
        layout.addRow("DSR/DTR", dsrdtr)

        widget.setLayout(layout)
        widget.params = {
            "port"      : port.text,
            "baudrate"  : baudrate.text,
            "bytesize"  : bytesize.currentText,
            "timeout"   : timeout.text,
            "parity"    : parity.currentText,
            "stopbits"  : stopbits.currentText,
            "xonoff"    : xonoff.isChecked,
            "dsrdtr"    : dsrdtr.isChecked
        }
        return widget

    def build_file_page(self) -> QWidget:
        widget = QWidget()
        layout = QFormLayout() 
        widget.params = {}

        file = QLineEdit("/dev/usb/lp0")
        layout.addRow("File", file)

        flush = QCheckBox()
        flush.setChecked(True)
        layout.addRow("Auto-flush", flush)

        widget.setLayout(layout)
        widget.params = {"file" : file.text, "flush" : flush.isChecked}
        return widget


def main():
    app = MainApp(sys.argv)
    window = MainWindow()

    desktop = QDesktopWidget().availableGeometry()
    width = (desktop.width() - window.width()) / 2
    height = (desktop.height() - window.height()) / 2
    window.show()
    window.move(width, height)

    sys.exit(app.exec_())
