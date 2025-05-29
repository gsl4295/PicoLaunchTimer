# For basic board functions
try:
    from board_definitions.raspberry_pi_pico_w import GP10, GP11, GP16, GP17, GP18, LED
except ImportError:  # pragma: no cover
    # noinspection PyPackageRequirements
    from board import GP10, GP11, GP16, GP17, GP18, GP0, LED
from busio import SPI
from digitalio import DigitalInOut, Direction, Pull

# For screen
from displayio import release_displays, Group, Bitmap, Palette, TileGrid
from terminalio import FONT
from fourwire import FourWire
from adafruit_display_text import label, outlined_label
from adafruit_display_text.scrolling_label import ScrollingLabel
from adafruit_st7735r import ST7735R

# For wifi connection
from wifi import radio
import socketpool
import ssl
from os import getenv

# For countdown functionality
import adafruit_requests
from adafruit_datetime import datetime, timedelta  # timezone
from time import sleep

print("System on internal power")

class PicoControl:
    def __init__(self):
        self.counter = 0
        mosi_pin = GP11
        clk_pin = GP10
        reset_pin = GP17
        cs_pin = GP18
        dc_pin = GP16
        release_displays()
        spi = SPI(clock=clk_pin, MOSI=mosi_pin)
        display_bus = FourWire(spi, command=dc_pin, chip_select=cs_pin, reset=reset_pin)
        self.display = ST7735R(display_bus, width=128, height=160, bgr=True)
        self.led = DigitalInOut(LED)
        self.led.direction = Direction.OUTPUT
        self.pool = socketpool.SocketPool(radio)
        self.requests = adafruit_requests.Session(self.pool, ssl.create_default_context())
        self.launch: str = ""
        self.name: str = ""
        self.t0: str = ""
        self.win_open: str = ""
        self.win_close: str = ""
        self.provider: str = ""
        self.vehicle: str = ""
        self.pad: str = ""
        self.lc: str = ""
        self.country: str = ""
        self.y: str = ""
        self.m: str = ""
        self.d: str = ""
        self.h: str = ""
        self.mi: str = ""
        self.button = DigitalInOut(GP0)
        self.button.direction = Direction.INPUT
        self.button.pull = Pull.DOWN
        self.manual_setting: bool = False
        self.utc_delta = timedelta(hours=5)  # Change in timezone from UTC

    def led_toggle(self, toggle: bool) -> None:
        self.led.value = toggle

    def visuals(self, hexcode: str):
        # Add purple background
        self.splash = Group()
        self.display.root_group = self.splash
        color_bitmap = Bitmap(128, 160, 1)
        color_palette = Palette(1)
        color_palette[0] = int("0x" + hexcode, 16)
        bg_sprite = TileGrid(color_bitmap, pixel_shader=color_palette, x=0, y=0)
        self.splash.append(bg_sprite)

        # Create black rectangle
        # This visually makes the purple background look like just a border
        inner_bitmap = Bitmap(118, 150, 1)
        inner_palette = Palette(1)
        inner_palette[0] = 0x000000  # Black
        inner_sprite = TileGrid(inner_bitmap, pixel_shader=inner_palette, x=5, y=5)
        self.splash.append(inner_sprite)

        parsed_color = int("0x" + hexcode, 16)

        self.countdown_text_group = Group(scale=2, x=16, y=26)
        self.countdown_text_area = label.Label(FONT, text="", color=0xFFFFFF)
        self.countdown_text_group.append(self.countdown_text_area)
        self.splash.append(self.countdown_text_group)

        max_char = 20

        self.main_text_group = Group(scale=1, x=16, y=50)
        self.main_row_1 = ScrollingLabel(FONT, y=0, text=f"", color=parsed_color, max_characters=max_char)
        self.main_row_2 = ScrollingLabel(FONT, y=15, text=f"", color=parsed_color, max_characters=max_char)
        self.main_row_3 = ScrollingLabel(FONT, y=30, text=f"", color=parsed_color, max_characters=max_char)
        self.main_row_4 = ScrollingLabel(FONT, y=45, text=f"", color=parsed_color, max_characters=max_char)
        self.main_row_5 = ScrollingLabel(FONT, y=60, text=f"PicoLaunchTimer", color=parsed_color,
                                         max_characters=max_char)
        self.main_row_6 = label.Label(FONT, y=75, text=f"Version 0.2", color=parsed_color)
        self.main_row_7 = label.Label(FONT, y=90, text=f"Loading...", color=parsed_color)
        self.main_text_group.append(self.main_row_1)
        self.main_text_group.append(self.main_row_2)
        self.main_text_group.append(self.main_row_3)
        self.main_text_group.append(self.main_row_4)
        self.main_text_group.append(self.main_row_5)
        self.main_text_group.append(self.main_row_6)
        self.main_text_group.append(self.main_row_7)
        self.splash.append(self.main_text_group)

        print(f"Screen rendered with an accent of hexcode {hexcode}")

    def update_scrolls(self):
        self.main_row_1.update()
        self.main_row_2.update()
        self.main_row_3.update()
        self.main_row_4.update()
        self.main_row_5.update()

    def wifi_connect(self):
        while True:
            try:
                radio.connect(getenv("WIFI"), getenv("PASS"))
                print(f"Connected to the Internet via {getenv("WIFI")}")
                break
            except ConnectionError:
                continue
            print("No connection, trying again in 2 seconds")
            sleep(2)

    def get_launch_info(self):
        self.response = self.requests.get("https://fdo.rocketlaunch.live/json/launches/next/1")
        self.content = self.response.json()
        try:
            self.launch = self.content["result"][0]
            self.t0 = self.launch["t0"]  # Define t0 first here to avoid error with countdown loop *Temporary fix*
            self.name = self.launch["name"]
            self.vehicle = self.launch["vehicle"]["name"]
            self.pad = self.launch["pad"]["name"]
            self.lc = self.launch["pad"]["location"]["name"]
            self.country = self.launch["pad"]["location"]["country"]
        except AttributeError as ae:
            self.launch = "LAUNCH_INFO_ERROR"

    def define_auto_vars(self):  # Separate function simply for running during main countdown loop
        self.t0 = self.launch["t0"]
        self.name = self.launch["name"]
        self.vehicle = self.launch["vehicle"]["name"]
        self.pad = self.launch["pad"]["name"]
        self.lc = self.launch["pad"]["location"]["name"]
        self.country = self.launch["pad"]["location"]["country"]

        d, t = self.t0[:-1].split("T")
        self.y, self.m, self.dy = d.split("-")
        self.h, self.mi = t.split(":")

    def json_error_handling(self):
        # If an official T-0 time isn't listed, but a window opening time is, use it instead
        if self.t0 is None and self.win_open is not None:
            print("Error: Found no T-0 time. Proceeding with window opening time")
            self.t0 = self.win_open

    def manual_launch_info(self):
        # Variables in order of display on screen
        self.t0 = "2025-09-25T05:00Z"  # T-0 time is formatted as "YYYY-MM-DDTHH:MMZ". Input time should be in UTC.
        self.name = "Flight 9"
        self.vehicle = "Starship"
        self.pad = "OLIT-A"
        self.lc = "Starbase, TX"
        self.country = "United States"

        d, t = self.t0[:-1].split("T")
        self.y, self.m, self.dy = d.split("-")
        self.h, self.mi = t.split(":")

    def countdown_loop(self, http_time: int, display_interval: int):
        if self.manual_setting:
            self.manual_launch_info()
        elif not self.manual_setting:
            self.define_auto_vars()
        else:
            pass
        self.utc_launch_time = datetime(int(self.y), int(self.m), int(self.dy), int(self.h), int(self.mi))
        self.full_launch_time = self.utc_launch_time - self.utc_delta
        self.launch_date = str(self.full_launch_time).split(" ")[0]

        num_cycles = int(http_time / display_interval)

        for _ in range(num_cycles):
            if self.button.value:
                print("Button pressed, acquiring the newest data")
                self.countdown_text_area.text = f"Loading"
                sleep(1)
                if self.manual_setting:
                    self.manual_setting = False
                    return
                else:
                    self.manual_setting = True
                    return

            current_time = datetime.now()  # try .astimezone()
            countdown = self.full_launch_time - current_time

            total_seconds = int(countdown.total_seconds())
            days = total_seconds // 86400
            hours = total_seconds // 3600
            minutes = (total_seconds % 3600) // 60
            seconds = total_seconds % 60

            if hours == 0:
                hour_logic = ""
            else:
                hour_logic = f"{hours}:"

            if hours >= 100:
                countdown_str = f"{days} Days"
            elif total_seconds <= 0:
                countdown_str = f"00:00"
            else:
                countdown_str = f"{hour_logic}{minutes:02}:{seconds:02}"

            countdown_str = countdown_str.split('.')[0]

            self.main_row_1.text = f"{self.name}"
            self.main_row_2.text = f"{self.vehicle}"
            self.main_row_3.text = f"{self.pad}"
            self.main_row_4.text = f"{self.lc}"
            self.main_row_5.text = f"{self.country}"
            self.main_row_6.text = f"{self.launch_date}"
            self.main_row_7.text = f"Manual: {self.manual_setting}"

            self.countdown_text_area.text = f"{countdown_str}"

            self.counter += 1
            if self.counter == 1:
                print(f"Countdown active, manual flag set to {self.manual_setting}")
            elif self.counter / 10 == round(self.counter / 10):
                pass

            self.update_scrolls()

            sleep(display_interval)

    def run_loop(self, setting: bool,
                 hexcode="47D700"):  # setting argument is just for the initial mode or if you don't have a button
        self.led_toggle(False)
        self.visuals(hexcode)
        self.wifi_connect()
        self.manual_setting = setting

        while True:
            if self.manual_setting:
                pass
            else:
                self.get_launch_info()
            self.json_error_handling()
            self.countdown_loop(120, 0.1)


control = PicoControl()
control.run_loop(True)
