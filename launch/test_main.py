from sys import modules
from types import ModuleType
from unittest import TestCase, main
from unittest.mock import MagicMock


class TestMain(TestCase):
    class FakePin:
        def switch_to_output(self, value): pass

    # *** Here are a few convenience classes that minimally mock the actual implementation
    class FakeSocket:
        pass
    #     def __init__(self, *_):
    #         pass
    #         # self.settimeout = lambda _x: None
    #         # self.sendto = lambda _x, _y: None
    #
    #     # noinspection PyMethodMayBeStatic
    #     def recv_into(self, x):
    #         x[:] = (
    #             b'\x1c\x02\x03\xe8\x00\x00\x02Z\x00\x00\n\xf4\xc7f.F\xeb\x9e\x85\x85\x01s;m\x00'
    #             b'\x00\x00\x00\x00\x00\x00\x00\xeb\x9e\x8cd\xa7z\xf7\r\xeb\x9e\x8cd\xa7\x82w\xf6'
    #         )
    #
    #     # def __enter__(self):
    #     #     return self
    #
    #     # def __exit__(self, exc_type, exc_value, traceback):
    #     #     pass

    class FakeSocketPool:
        AF_INET = None
        SOCK_DGRAM = None

        def __init__(self, *_):
            self.getaddrinfo = lambda _x, _y: [[0, 0, 0, 0, 0]]
            self.socket = lambda _x, _y: TestMain.FakeSocket()

    class FakeResponse:
        def __init__(self, json_response_data):
            self.json_response_data = json_response_data

        def json(self):
            return self.json_response_data

        def close(self):
            pass

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
        fake_dio.DigitalInOut = MagicMock(return_value=TestMain.FakePin())
        fake_dio.Direction = MagicMock()
        fake_dio.Pull = MagicMock()
        modules["digitalio"] = fake_dio

        fake_displayio = ModuleType("displayio")
        fake_displayio.release_displays = MagicMock(return_value=TestMain.FakePin())
        fake_displayio.Group = MagicMock(return_value=TestMain.FakePin())
        fake_displayio.Bitmap = MagicMock(return_value=TestMain.FakePin())
        fake_displayio.Palette = MagicMock(return_value=TestMain.FakePin())
        fake_displayio.TileGrid = MagicMock(return_value=TestMain.FakePin())
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

        # fake_conn_manager = ModuleType("adafruit_connection_manager")
        # fake_conn_manager.get_radio_socketpool = MagicMock(return_value=TestMain.FakeSocketPool())
        # fake_conn_manager.get_radio_ssl_context = MagicMock(return_value=MagicMock())
        # modules["adafruit_connection_manager"] = fake_conn_manager

        fake_requests = ModuleType("adafruit_requests")
        cls.fake_session_instance = MagicMock()
        cls.fake_session_instance.get = MagicMock(name="get")
        fake_requests.Session = MagicMock(return_value=cls.fake_session_instance)
        modules["adafruit_requests"] = fake_requests

        from launch.main import PicoControl
        cls.control = PicoControl

    def test_get_launch_info(self):
        p = self.control()
        # call it once with valid response data
        self.fake_session_instance.get.return_value = TestMain.FakeResponse(
            {
                "result": [
                    {
                        "name": "Ax-4",
                        "provider": {"name": "SpaceX"},
                        "vehicle": {"name": "Falcon 9"},
                        "pad": {
                            "name": "LC-39A",
                            "location": {
                                "name": "Kennedy Space Center",
                                "state": "FL",
                                "statename": "Florida",
                                "country": "United States",
                            }
                        },
                        "missions": [{"name": "Ax-4"}],
                        "win_open": None,
                        "t0": "2025-06-10T12:22Z",
                        "win_close": None,
                    }
                ]
            }
        )
        p.get_launch_info()
        self.assertIsInstance(p.launch, dict)
        self.assertEqual("2025-06-10T12:22Z", p.launch["t0"])
        # then call it with empty response data
        self.fake_session_instance.get.return_value = TestMain.FakeResponse({})
        p.get_launch_info()
        self.assertEqual("ERROR t0", p.launch["t0"])

    def test_define_auto_vars(self):
        p = self.control()
        p.launch = {
            "name": "Ax-4",
            "provider": {"name": "SpaceX"},
            "vehicle": {"name": "Falcon 9"},
            "pad": {
                "name": "LC-39A",
                "location": {
                    "name": "Kennedy Space Center",
                    "state": "FL",
                    "statename": "Florida",
                    "country": "United States",
                }
            },
            "missions": [{"name": "Ax-4"}],
            "win_open": "2025-06-10T12:00Z",
            "t0": "2025-06-10T12:22Z",
            "win_close": "2025-06-10T13:00Z",
        }
        p.define_auto_vars()
        self.assertEqual("2025-06-10T12:22Z", p.t0)
        p.launch["t0"] = None
        p.define_auto_vars()
        self.assertEqual("2025-06-10T12:00Z", p.t0)

    def test_manual_launch_info(self):
        p = self.control()
        p.manual_launch_info()
        self.assertNotEqual("", p.t0)

    def test_manage_memory(self):
        # test it once with verbose and one not
        #p = self.control()
        pass

    def test_countdown_loop(self):
        pass

    def test_run_loop(self):
        pass  # probably want to add an argument to run it once without the countdown loop

    def test_get_utc_delta(self):
        pass

    def test_wifi_connected(self):
        pass

    def test_update_scrolls(self):
        pass

    def test_visuals(self):
        pass

    def test_led_toggle(self):
        pass


if __name__ == "__main__":  # pragma: no cover
    main()
