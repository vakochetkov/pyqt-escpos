import typing
import os.path

from PyQt5.QtCore import QRegExp, Qt
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
            self.addTo(f"Text <{pteText.toPlainText()}>")
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
            self.addTo(f"Block text <{leTextColumns.text()}> <{pteText.toPlainText()}>")
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

        lblHighDensity = QLabel("High density")
        cbVertical = QCheckBox("Vertical")
        cbVertical.setChecked(True)
        cbHorizontal = QCheckBox("Horizontal")
        cbHorizontal.setChecked(True)
        layout.addWidget(lblHighDensity, 1, 0, 1, 1) 
        layout.addWidget(cbVertical, 1, 1, 1, 1) 
        layout.addWidget(cbHorizontal, 1, 2, 1, 1) 

        lblFragmentHeight = QLabel("Fragment height")
        leFragmentHeight = QLineEdit("1024")
        decimalValidator = QRegExpValidator(QRegExp("[0-9]+"))
        leFragmentHeight.setValidator(decimalValidator)
        layout.addWidget(lblFragmentHeight, 2, 0, 1, 1) 
        layout.addWidget(leFragmentHeight, 2, 1, 1, 1) 

        btnImagePrint = QPushButton("Print")
        layout.addWidget(btnImagePrint, 2, 2, 1, 1) 

        printImage = lambda: self.__printImage(
            leImagePath.text(),
            highDensityVertical=cbVertical.isChecked(),
            highDensityHorizontal=cbHorizontal.isChecked(),
            fragmentHeight=leFragmentHeight.text()
        )
        btnImagePrint.clicked.connect(printImage)

        layout.setAlignment(Qt.AlignTop)
        w.setLayout(layout)
        return w

    def __printImage(self, path: str, highDensityVertical: bool, highDensityHorizontal: bool,
                    fragmentHeight: int):
        if os.path.isfile(path):
            self.printer.image(
                path, 
                high_density_vertical=bool(highDensityVertical), 
                high_density_horizontal=bool(highDensityHorizontal), 
                fragment_height=int(fragmentHeight)
            )
            self.addTo(f"Image {path}")
        else:
           self.__showError("Image path is not a file!")           

    def __openImage(self) -> str:
        path, accepted = QFileDialog.getOpenFileName(self, 'Open image')
        if accepted:
            return os.path.abspath(path)
        else:
            self.__showError("No path selected")
            return ""

    def __showError(self, error: str) -> None:
        mb = QMessageBox()
        mb.setIcon(QMessageBox.Icon.Error)
        mb.setWindowTitle("Error")
        mb.setText(f"{msg}")
        mb.setStandardButtons(QMessageBox.Ok)
        mb.exec_()

    def __buildTabQR(self) -> QWidget:
        ecMap = {"L": 0, "M": 1, "Q": 2, "H": 3}
        modelMap = {"1": 1, "2": 2, "MICRO": 3}

        w = QWidget()
        layout = QFormLayout()

        leContent = QLineEdit("123456789")
        layout.addRow("QR content", leContent)

        cmbErrorCorrection = QComboBox()
        cmbErrorCorrection.addItems(list(ecMap.keys()))
        layout.addRow("Error correction", cmbErrorCorrection)

        cmbModel = QComboBox()
        cmbModel.addItems(list(modelMap.keys()))
        cmbModel.setCurrentIndex(2 - 1)
        layout.addRow("Code model", cmbModel)

        cmbSize = QComboBox()
        cmbSize.addItems(map(str, range(1,17)))
        cmbSize.setCurrentIndex(3 - 1)
        layout.addRow("Size", cmbSize)

        btnPrint = QPushButton("Print")
        layout.addRow(btnPrint)

        printQR = lambda: (
            self.printer.qr(
                leContent.text(),
                ec=int(ecMap[cmbErrorCorrection.currentText()]),
                model=int(modelMap[cmbModel.currentText()]),
                size=int(cmbSize.currentText())
            ),
            self.addTo(f"QR {leContent.text()}")
        )
        btnPrint.clicked.connect(printQR)

        w.setLayout(layout)
        return w

    def __buildTabBarcode(self) -> QWidget:
        w = QWidget()
        layout = QFormLayout()

        leContent = QLineEdit("123456789")
        layout.addRow("Barcode content", leContent)

        cmbFormat = QComboBox()
        cmbFormat.addItems([
            "UPC-A", "UPC-E", "EAN13", "EAN8", "CODE39", "ITF", "NW7", "CODE93", "CODE128"
        ]) # NW7 is not supported by QR701
        layout.addRow("Format", cmbFormat)

        cmbHeight = QComboBox()
        cmbHeight.addItems(map(str, range(1,256))) # default 64
        cmbHeight.setCurrentIndex(64 - 1)
        layout.addRow("Height", cmbHeight)

        cmbWidth = QComboBox()
        cmbWidth.addItems(map(str, range(2,7))) # default 3
        cmbWidth.setCurrentIndex(3 - 2)
        layout.addRow("Width", cmbWidth)

        cmbPos = QComboBox()
        cmbPos.addItems([
            "BELOW", "ABOVE", "BOTH", "OFF"
        ]) # default BELOW
        layout.addRow("Pos", cmbPos)

        cmbFont = QComboBox()
        cmbFont.addItems(["A", "B"]) # default A
        layout.addRow("Font", cmbFont)

        cbAlignCenter = QCheckBox()
        cbAlignCenter.setChecked(True)
        layout.addRow("Align center", cbAlignCenter)

        btnPrint = QPushButton("Print")
        layout.addRow(btnPrint)

        printBarcode = lambda: (
            self.printer.barcode(
                leContent.text(),
                cmbFormat.currentText(),
                height=int(cmbHeight.currentText()),
                width=int(cmbWidth.currentText()),
                pos=str(cmbPos.currentText()),
                font=str(cmbFont.currentText()),
                align_ct=bool(cbAlignCenter.isChecked())
            ),
            self.addTo(f"Barcode {cmbFormat.currentText()} {leContent.text()}")
        )
        btnPrint.clicked.connect(printBarcode)

        w.setLayout(layout)
        return w
