from sys import modules
from types import ModuleType
from unittest import TestCase, main
from unittest.mock import MagicMock


class TestMain(TestCase):
    class FakePin:
        def switch_to_output(self, value): pass

    # *** Here are a few convenience classes that minimally mock the actual implementation
    class FakeSocket:
        def __init__(self, *_):
            self.settimeout = lambda _x: None
            self.sendto = lambda _x, _y: None

        # noinspection PyMethodMayBeStatic
        def recv_into(self, x):
            x[:] = (
                b'\x1c\x02\x03\xe8\x00\x00\x02Z\x00\x00\n\xf4\xc7f.F\xeb\x9e\x85\x85\x01s;m\x00'
                b'\x00\x00\x00\x00\x00\x00\x00\xeb\x9e\x8cd\xa7z\xf7\r\xeb\x9e\x8cd\xa7\x82w\xf6'
            )

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc_value, traceback):
            pass

    class FakeSocketPool:
        AF_INET = None
        SOCK_DGRAM = None

        def __init__(self, *_):
            self.getaddrinfo = lambda _x, _y: [[0, 0, 0, 0, 0]]
            self.socket = lambda _x, _y: TestMain.FakeSocket()

    @classmethod
    def setUpClass(cls):
        mock_board = ModuleType('board_definitions.raspberry_pi_pico_w')
        mock_board.GP0 = TestMain.FakePin()
        mock_board.GP10 = TestMain.FakePin()
        mock_board.GP11 = TestMain.FakePin()
        mock_board.GP16 = TestMain.FakePin()
        mock_board.GP17 = TestMain.FakePin()
        mock_board.GP18 = TestMain.FakePin()
        mock_board.LED = TestMain.FakePin()
        modules['board_definitions.raspberry_pi_pico_w'] = mock_board

        cls.fake_wifi = ModuleType("wifi")
        cls.fake_wifi.radio = MagicMock(name="radio")
        modules["wifi"] = cls.fake_wifi

        fake_dio = ModuleType("digitalio")
        fake_dio.DigitalInOut = MagicMock(return_value = TestMain.FakePin())
        fake_dio.Direction = MagicMock()
        fake_dio.Pull = MagicMock()
        modules["digitalio"] = fake_dio

        fake_displayio = ModuleType("displayio")
        fake_displayio.release_displays = MagicMock(return_value = TestMain.FakePin())
        fake_displayio.Group = MagicMock(return_value = TestMain.FakePin())
        fake_displayio.Bitmap = MagicMock(return_value = TestMain.FakePin())
        fake_displayio.Palette = MagicMock(return_value = TestMain.FakePin())
        fake_displayio.TileGrid = MagicMock(return_value = TestMain.FakePin())
        modules["displayio"] = fake_displayio

        fake_terminalio = ModuleType("terminalio")
        fake_terminalio.FONT = MagicMock()
        modules["terminalio"] = fake_terminalio

        fake_fourwire = ModuleType("fourwire")
        fake_fourwire.FourWire = MagicMock()
        modules["fourwire"] = fake_fourwire

        fake_7735 = ModuleType("adafruit_st7735r")
        fake_7735.ST7735R = MagicMock()
        modules["adafruit_st7735r"] = fake_7735

        fake_socketpool = ModuleType("socketpool")
        fake_socketpool.SocketPool = MagicMock(return_value=TestMain.FakeSocketPool())
        modules["socketpool"] = fake_socketpool

        fake_busio = ModuleType("busio")
        fake_busio.SPI = MagicMock()
        modules["busio"] = fake_busio


        from launch.main import PicoControl
        cls.control = PicoControl

    def test_a(self):
        p = self.control()


if __name__ == "__main__":
    main()