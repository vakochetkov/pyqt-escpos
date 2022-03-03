import typing
import os.path

from PyQt5.QtCore import QRegExp
from PyQt5.QtGui import QRegExpValidator

from PyQt5.QtWidgets import (
    QWidget, QTabWidget, QFrame, QHBoxLayout, QGridLayout, QFormLayout,
    QPushButton, QLabel, QLineEdit, QCheckBox, QComboBox, QPlainTextEdit,
    QFileDialog
)

from printer import Printer


class Tabs(QTabWidget):
    def __init__(self, printer: Printer, addTo: typing.Callable[[str], None], parent = None) -> None:
        super(Tabs, self).__init__(parent)

        self.printer = printer
        self.addTo = addTo

        self.addTab(self.__buildTabText(), "Text")
        self.addTab(self.__buildTabImage(), "Image")
        self.addTab(self.__buildTabQR(), "QR")
        self.addTab(self.__buildTabBarcode(), "Barcode")

    def __buildTabText(self) -> QWidget:
        w = QWidget()

        layoutPrint = QGridLayout()
        layoutPrint.addWidget(QLabel("Print"), 0, 0)

        leTextLine = QLineEdit("One line to print")
        layoutPrint.addWidget(leTextLine, 1, 0, 1, 3)    

        printLine = lambda: (
            self.printer.textline(str(leTextLine.text())), 
            self.addTo(f"Line <{str(leTextLine.text())}>...")
        )

        btnPrintLine = QPushButton("Print line")
        btnPrintLine.clicked.connect(printLine)
        layoutPrint.addWidget(btnPrintLine, 1, 3, 1, 1)

        printMultiLine = lambda: (
            self.printer.text(str(pteText.toPlainText())),
            self.addTo(f"Text <{pteText.toPlainText()}...>")
        )

        pteText = QPlainTextEdit("Multiple\nlines\nto\nprint\n")
        layoutPrint.addWidget(pteText, 2, 0, 1, 4)

        btnAnyText = QPushButton("Print as is")
        btnAnyText.clicked.connect(printMultiLine)
        layoutPrint.addWidget(btnAnyText, 3, 3)

        layoutPrint.addWidget(QLabel("Columns:"), 3, 0)

        columnsValidator = QRegExpValidator(QRegExp("[0-9]+"))
        leTextColumns = QLineEdit("16")
        leTextColumns.setValidator(columnsValidator)
        layoutPrint.addWidget(leTextColumns, 3, 1)

        printBlockText = lambda: (
            self.printer.block_text(str(pteText.toPlainText()), int(leTextColumns.text())),
            self.addTo(f"Block text <{leTextColumns.text()}> <{pteText.toPlainText()}>...")
        )

        btnBlockText = QPushButton("Print in specified columns")
        btnBlockText.clicked.connect(printBlockText)
        layoutPrint.addWidget(btnBlockText, 3, 2)

        layoutParams = QFormLayout()
        layoutParams.addRow(QLabel("With parameters"))

        cmbAlign = QComboBox()
        cmbAlign.addItems(["Left", "Center", "Right"])
        cmbAlign.setCurrentIndex(0)
        layoutParams.addRow("Align:", cmbAlign)

        cmbFont = QComboBox()
        cmbFont.addItems(["A", "B"])
        cmbFont.setCurrentIndex(0)
        layoutParams.addRow("Font:", cmbFont)

        textTypeMap = {
            "Normal": "NORMAL", 
            "Bold": "B",
            "Underlined": "U",
            "Underlined v2": "U2",
            "Bold & Underlined": "BU",
            "Bold & Underlined v2": "BU2"
        }
        cmbTextType = QComboBox()
        cmbTextType.addItems(textTypeMap.keys())
        cmbTextType.setCurrentIndex(0)
        layoutParams.addRow("Text type:", cmbTextType)

        cmbWidth = QComboBox()
        cmbWidth.addItems(map(str, list(range(1,9))))
        cmbWidth.setCurrentIndex(0)
        layoutParams.addRow("Width:", cmbWidth)

        cmbHeight = QComboBox()
        cmbHeight.addItems(map(str, list(range(1,9))))
        cmbHeight.setCurrentIndex(0)
        layoutParams.addRow("Height:", cmbHeight)

        densityMap = {
            "Default": 9,
            "0": 0,
            "1": 1,
            "2": 2,
            "3": 3,
            "4": 4,
            "5": 5,
            "6": 6,
            "7": 7,
            "8": 8,
        }
        cmbDensity = QComboBox()
        cmbDensity.addItems(densityMap.keys())
        cmbHeight.setCurrentIndex(0)
        layoutParams.addRow("Density:", cmbDensity)

        cbInvert = QCheckBox()
        cbSmooth = QCheckBox()
        cbFlip = QCheckBox()
        cbInvert.setChecked(False)
        cbSmooth.setChecked(False)
        cbFlip.setChecked(False)
        layoutParams.addRow("Invert:", cbInvert)
        layoutParams.addRow("Smooth:", cbSmooth)
        layoutParams.addRow("Flip:", cbFlip)

        setParams = lambda: (
            self.printer.set(
                align=str(cmbAlign.currentText()),
                font=str(cmbFont.currentText()),
                text_type=str(textTypeMap[cmbTextType.currentText()]),
                width=int(cmbWidth.currentText()),
                height=int(cmbHeight.currentText()),
                density=int(densityMap[cmbDensity.currentText()]),
                invert=bool(cbInvert.isChecked()),
                smooth=bool(cbSmooth.isChecked()),
                flip=bool(cbFlip.isChecked()),
            ),
            self.addTo("Set text parameters")
        )

        btnApply = QPushButton("Set")
        btnApply.clicked.connect(setParams)
        layoutParams.addRow(btnApply)

        layout = QHBoxLayout()
        layout.setSpacing(15)

        layout.addLayout(layoutPrint)
        separator = QFrame()
        separator.setFrameShape(QFrame.VLine)
        separator.setFrameShadow(QFrame.Sunken)
        layout.addWidget(separator)
        layout.addLayout(layoutParams)

        w.setLayout(layout)
        return w

    def __buildTabImage(self) -> QWidget:
        w = QWidget()
        layout = QGridLayout()

        leImagePath = QLineEdit()
        btnImageSelect = QPushButton("...")

        imageSelect = lambda: leImagePath.setText(str(self.__openImage()))
        btnImageSelect.clicked.connect(imageSelect)

        layout.addWidget(leImagePath, 0, 0, 1, 3) 
        layout.addWidget(btnImageSelect, 0, 3, 1, 1)
        #     def open_file(self):
        # """Open a QFileDialog to allow the user to open a file into the application."""
        # filename, accepted = QFileDialog.getOpenFileName(self, 'Open File')

        # if accepted:
        #     with open(filename) as file:
        #         file.read()

        w.setLayout(layout)
        return w

    def __openImage(self) -> str:
        path, accepted = QFileDialog.getOpenFileName(self, 'Open image')
        # if accepted:
        #     try:
        #         self.printer.image()
        return os.path.abspath(path)

    def __buildTabQR(self) -> QWidget:
        w = QWidget()
        return w

    def __buildTabBarcode(self) -> QWidget:
        w = QWidget()
        return w
