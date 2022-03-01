from escpos.constants import *
from escpos.printer import Usb, Dummy

class Printer(object):
    def __init__(self, vid, pid, timeout=0) -> None:
        self.printer = Usb(vid, pid, timeout)
        self.buf = Dummy()

    def text(self, text) -> None:
        self.buf.text(f"{text}")

    def textline(self, text: str) -> None:
        self.buf.text(f"{text}\n")

    def block_text(self, text: str, columns=None) -> None:
        self.buf.block_text(text, columns)

    def image(self, img_source, high_density_vertical=True, high_density_horizontal=True,
        impl="bitImageRaster", fragment_height=1024) -> None:
        self.buf.image(img_source, high_density_vertical, high_density_horizontal, impl, fragment_height)

    def qr(self, content, ec=QR_ECLEVEL_L, size=3, model=QR_MODEL_2, native=False) -> None:
        self.buf.qr(content, ec, size, model, native)

    def barcode(self, code, bc, height=64, width=3, pos="BELOW", font="A", align_ct=True, function_type="A") -> None:
        self.buf.barcode(code, bc, height, width, pos, font, align_ct, function_type)

    def cut(self) -> None:
        self.buf.cut()

    def line_spacing(self, spacing=None, divisor=180) -> None:
        self.buf.line_spacing(spacing, divisor)

    def set(self, align='left', font='a', text_type='normal', width=1, height=1,
        density=9, invert=False, smooth=False, flip=False) -> None:
        self.printer.set(align, font, text_type, width, height, density, invert, smooth, flip)

    def charset(self, charset: str):
        self.printer.charcode(charset)

    def output(self) -> None:
        #print(str(self.buf.output))
        self.printer._raw(self.buf.output)


if __name__ == "__main__":
    print("Test Printer.py\n" + "=" * 20)
    # USB id for QR701
    VID = 0x28E9
    PID = 0x0289

    p = Printer(VID, PID)
    p.set(align='center', text_type="BU", width=4, height=4)
    p.textline("Привет 123!")
    p.output()