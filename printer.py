import logging
import typing

from escpos.constants import *
from escpos.printer import Usb, Network, Serial, File, Dummy


logger = logging.getLogger(__name__)

PRINTER_TYPES = ("USB", "Network", "Serial", "File")
SERIAL_PARITIES  = ('N', 'E', 'O', 'M', 'S')
SERIAL_STOPBITS  = (1, 1.5, 2)
SERIAL_BYTESIZES = (5, 6, 7, 8)


class PrinterBuilder(object):
    def __init__(self):
        self.printer: typing.Union[None, Usb, Network, Serial, File] = None
    
    def build(self, printer_type: str, **kwargs) -> bool:
        result = False
        if printer_type in PRINTER_TYPES:
            try:
                if printer_type == "USB":
                    vid = int(kwargs.get("vid"), 16)
                    pid = int(kwargs.get("pid"), 16)
                    timeout = int(kwargs.get("timeout"))

                    self.printer = Usb(vid, pid, timeout=timeout)
                    return True
                elif printer_type == "Network":
                    host = str(kwargs.get("host"))
                    port = int(kwargs.get("port"))
                    timeout = int(kwargs.get("timeout"))
                    
                    self.printer = Network(host, port=port, timeout=timeout)
                    return True
                elif printer_type == "Serial":
                    port        = str(kwargs.get("port"))
                    baudrate    = int(kwargs.get("baudrate"))
                    bytesize    = int(kwargs.get("bytesize"))
                    timeout     = int(kwargs.get("timeout"))
                    parity      = str(kwargs.get("parity"))
                    stopbits    = float(kwargs.get("stopbits"))
                    xonoff      = bool(kwargs.get("xonoff"))
                    dsrdtr      = bool(kwargs.get("dsrdtr"))
                    
                    self.printer = Serial(
                        port, baudrate=baudrate, bytesize=bytesize, timeout=timeout,
                        parity=parity, stopbits=stopbits, xonxoff=xonoff, dsrdtr=dsrdtr
                    )
                    return True
                elif printer_type == "File":
                    file = kwargs.get("file")
                    flush = kwargs.get("flush")
                    
                    self.printer = File(file, auto_flush=flush)    
                    return True    
            except:
                logger.error(f"Failed to build with type <{printer_type}>")        
        else:
            logger.error("Unknow printer type") 
        return result           

    def get(self) -> typing.Union[None, Usb, Network, Serial, File]:
        return self.printer


class Printer(object):
    """ Wrapper around python-escpos """

    def __init__(self, driver) -> None:
        self.printer = driver
        self.buf = Dummy()

    def make_new_buffer(self) -> None:
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
        logger.warning("line_spacing() not implementeed!")
        self.buf.line_spacing(spacing, divisor)

    def set(self, align='left', font='a', text_type='normal', width=1, height=1,
        density=9, invert=False, smooth=False, flip=False) -> None:
        self.buf.set(align, font, text_type, width, height, density, invert, smooth, flip)

    def charset(self, charset: str):
        self.buf.charcode(charset)

    def output(self) -> None:
        #print(str(self.buf.output))
        self.printer._raw(self.buf.output)