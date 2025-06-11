from sys import modules
from types import ModuleType
from unittest import TestCase, main
from unittest.mock import MagicMock

from adafruit_display_text.scrolling_label import ScrollingLabel
from adafruit_display_text import label
from fontio import FontProtocol
from terminalio import FONT


class TestMain(TestCase):
    class FakePin:
        def switch_to_output(self, value): pass

        def __setitem__(self, key, value):
            pass

        def append(self, value):
            pass

        def value(self):
            pass

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

    class FakeGC:
        def __init__(self):
            pass

        def mem_free(self):
            return 1

        def collect(self):
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
        cls.fake_wifi.radio = MagicMock(name="radio", return_value=[ConnectionError, None])
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

        fake_gc = ModuleType("gc")
        fake_gc.mem_free = MagicMock(TestMain.FakeGC().mem_free())
        fake_gc.collect = MagicMock()
        modules["gc"] = fake_gc

        from launch.main import PicoControl
        cls.control = PicoControl

    def test_get_launch_info(self): # Done
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

    def test_define_auto_vars(self): # Up to date
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
        self.assertEqual("2025-06-10T12:22Z", p.t0) # Checks that t0 is valid

        p.launch["t0"] = None
        p.define_auto_vars()
        self.assertEqual("2025-06-10T12:00Z", p.t0) # Checks that win_open takes the place of t0

    def test_get_utc_delta(self):
        p = self.control()
        p.time_response = {
            "dstActive": True
        }
        total_delta = p.get_utc_delta(country="America", zone="Chicago", st_delta=-6)
        self.assertEqual(total_delta, -5)
        p.time_response = {
            "dstActive": False
        }
        total_delta = p.get_utc_delta(country="America", zone="Chicago", st_delta=-6)
        self.assertEqual(total_delta, -5)
        pass

    def test_manual_launch_info(self): # Done
        p = self.control()
        p.manual_launch_info()
        self.assertNotEqual("", p.t0)

    def test_manage_memory(self): # Done
        p = self.control()
        old_mem, new_mem = p.manage_memory(verbose=False)
        self.assertEqual(old_mem, new_mem)
        old_mem, new_mem = p.manage_memory(verbose=True)
        self.assertEqual(old_mem, new_mem)
        pass

    #def test_countdown_loop(self):
        #p = self.control()
        #p.main_row_1 = ScrollingLabel(font=FONT)
        #p.main_row_2 = ScrollingLabel(font=FONT)
        #p.main_row_3 = ScrollingLabel(font=FONT)
        #p.main_row_4 = ScrollingLabel(font=FONT)
        #p.main_row_5 = ScrollingLabel(font=FONT)
        #p.main_row_6 = label.Label(font=FONT)
        #p.main_row_7 = label.Label(font=FONT)
        #p.countdown_text_area = label.Label(font=FONT)
        #p.button.value = False
        ## Manual countdown data set to true
        #p.manual_setting = True
        #p.countdown_loop()
        #pass

    #def test_run_loop(self):
        #p = self.control()
        #return_value = p.run_loop(loop=False)
        #self.assertEqual(return_value, False)
        #pass

    def test_wifi_connected(self):
        p = self.control()
        return_value = p.wifi_connect()
        self.assertEqual(return_value, "Connected")
        return_value = p.wifi_connect()
        self.assertEqual(return_value, "Connected")
        pass

    def test_update_scrolls(self):
        p = self.control()
        p.main_row_1 = ScrollingLabel(font=FONT)
        p.main_row_2 = ScrollingLabel(font=FONT)
        p.main_row_3 = ScrollingLabel(font=FONT)
        p.main_row_4 = ScrollingLabel(font=FONT)
        p.main_row_5 = ScrollingLabel(font=FONT)
        p.main_row_6 = label.Label(font=FONT)
        p.main_row_7 = label.Label(font=FONT)
        p.countdown_text_area = label.Label(font=FONT)
        return_value = p.update_scrolls()
        self.assertEqual(return_value, "Screen scrolled")
        pass

    #def test_visuals(self):
        #p = self.control()
        #p.visuals((71, 215, 0))
        #self.assertEqual(p.countdown_text_area.text, "")
        #self.assertEqual(p.main_row_7.text, "Loading...")
        #pass

    def test_led_toggle(self): # Done
        p = self.control()
        p.led_toggle(True)
        self.assertEqual(p.led.value, True)
        pass


if __name__ == "__main__":  # pragma: no cover
    main()
