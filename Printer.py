from escpos.printer import Usb, Dummy

# USB id for QR701
VID = 0x28E9
PID = 0x0289

class Printer(object):
    def __init__(self, vid, pid, timeout=0) -> None:
        self.printer = Usb(vid, pid, timeout)
        self.buf = Dummy()

    def text(self, text) -> None:
        self.buf.text(f"{text}")

    def line(self, text: str) -> None:
        self.buf.text(f"{text}\n")

    def cut(self) -> None:
        self.buf.cut()

    def output(self) -> None:
        self.printer._raw(self.buf.output)

if __name__ == "__main__":
    print("Test Printer.py\n" + "=" * 20)
    p = Printer(VID, PID)
    p.line("Привет 123!")
    p.line("Привет 123!")
    p.output()