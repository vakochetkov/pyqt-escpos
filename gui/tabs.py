import typing

from PyQt5.QtWidgets import (
    QWidget, QTabWidget, QFrame, QHBoxLayout, QGridLayout, QFormLayout,
    QPushButton, QLabel, QLineEdit, QCheckBox, QComboBox
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
            self.addTo("Set new text parameters")
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
        return w

    def __buildTabQR(self) -> QWidget:
        w = QWidget()
        return w

    def __buildTabBarcode(self) -> QWidget:
        w = QWidget()
        return w
