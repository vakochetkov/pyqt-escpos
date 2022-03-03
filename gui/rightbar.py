import typing

from PyQt5.QtWidgets import (
    QWidget,
    QListWidget,
    QLabel,
    QPushButton,
    QHBoxLayout,
    QVBoxLayout
)

from printer import Printer


class RightBar(QWidget):
    def __init__(self, printer: Printer, parent = None):
        super(RightBar, self).__init__(parent)

        self.printer = printer

        self.layout = QVBoxLayout()

        lblTitle = QLabel("Print queue:")
        self.layout.addWidget(lblTitle)

        self.listQueue = QListWidget()
        self.layout.addWidget(self.listQueue)

        self.btnCut = QPushButton("Cut")
        self.btnCut.clicked.connect(self.__cut_handler)
        self.layout.addWidget(self.btnCut)

        btnLayout = QHBoxLayout()
        self.btnPrint = QPushButton("Send to printer")
        self.btnPrint.clicked.connect(self.__print_handler)
        btnLayout.addWidget(self.btnPrint)

        self.btnClear = QPushButton("Clear")
        self.btnClear.clicked.connect(self.__clear_handler)
        btnLayout.addWidget(self.btnClear)

        self.layout.addLayout(btnLayout)
        self.setLayout(self.layout)

    def __cut_handler(self) -> None:
        self.printer.cut()
        self.listQueue.addItem("Cut paper")

    def __clear(self) -> None:
        self.printer.make_new_buffer() # inefficient
        self.listQueue.clear()

    def add_to_queue(self, text: str) -> None:
        self.listQueue.addItem(text)

    def __print_handler(self) -> None:
        self.printer.output()
        self.__clear()

    def __clear_handler(self) -> None:
        self.__clear()