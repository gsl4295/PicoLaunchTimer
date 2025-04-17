# This is the single class that controls the entire Pico's functions

# For basic board functions
try:
    from board_definitions.raspberry_pi_pico_w import GP10, GP11, GP16, GP17, GP18, LED
except ImportError:  # pragma: no cover
    # noinspection PyPackageRequirements
    from board import GP10, GP11, GP16, GP17, GP18, LED
from busio import SPI
from digitalio import DigitalInOut, Direction

# For screen
from displayio import release_displays, Group, Bitmap, Palette, TileGrid
from terminalio import FONT
from fourwire import FourWire
from adafruit_display_text import label
from adafruit_st7735r import ST7735R

# For wifi connection
from wifi import radio
import socketpool
import ssl
from os import getenv

# For countdown functionality
import adafruit_requests
from adafruit_datetime import datetime  # timezone
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
        print("Background created")

        # Create black rectangle
        # This visually makes the purple background look like just a border
        inner_bitmap = Bitmap(118, 150, 1)
        inner_palette = Palette(1)
        inner_palette[0] = 0x000000  # Black
        inner_sprite = TileGrid(inner_bitmap, pixel_shader=inner_palette, x=5, y=5)
        self.splash.append(inner_sprite)

        print("Inner rectangle created")

        # Next Spaceflight header
        header_text_group = Group(scale=1, x=16, y=18)
        header_text = "Next Spaceflight"
        header_text_area = label.Label(FONT, text=header_text, color=int("0x" + hexcode, 16))
        header_text_group.append(header_text_area)
        self.splash.append(header_text_group)

        print("Text created")

        # Large white countdown group, scaled 2x
        countdown_text_group = Group(scale=2, x=16, y=42)
        self.countdown_text_area = label.Label(FONT, text="", color=0xFFFFFF)
        countdown_text_group.append(self.countdown_text_area)
        self.splash.append(countdown_text_group)

        # Smaller colored info group below countdown group
        main_text_group = Group(scale=1, x=16, y=96)
        self.main_text_area = label.Label(FONT, text="\n\n\nLoading...", color=int("0x" + hexcode, 16))
        main_text_group.append(self.main_text_area)
        self.splash.append(main_text_group)

        print(f"Visuals created with an accent of hexcode {hexcode}")

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
            self.name = self.launch["name"]
            self.t0 = self.launch["t0"]
            self.win_open = self.launch["win_open"]
            self.win_close = self.launch["win_close"]
            self.provider = self.launch["provider"]["name"]
            self.vehicle = self.launch["vehicle"]["name"]
            self.pad = self.launch["pad"]["name"]
            self.lc = self.launch["pad"]["location"]["name"]
            self.country = self.launch["pad"]["location"]["country"]
        except AttributeError as ae:
            self.launch = "LAUNCH_INFO_ERROR"

    def json_error_handling(self):
        # If an official T-0 time isn't listed, but a window opening time is, use it instead
        if self.t0 is None and self.win_open is not None:
            print("Found no T-0 time")
            self.t0 = self.win_open

    def countdown_loop(self, http_time: int, display_interval: int, version: int):
        d, t = control.t0[:-1].split("T")
        y, m, dy = d.split("-")
        h, mi = t.split(":")
        launch_time = datetime(int(y), int(m), int(dy), int(h) - 5, int(mi))

        num_cycles = int(http_time / display_interval)

        for _ in range(num_cycles):
            current_time = datetime.now()  # .astimezone()
            countdown = launch_time - current_time

            total_seconds = int(countdown.total_seconds())
            days = total_seconds // 86400
            hours = (total_seconds % 86400) // 3600
            minutes = (total_seconds % 3600) // 60
            seconds = total_seconds % 60

            if days > 1:
                day_logic = f"{days} days"
            elif days == 1:
                day_logic = f"{days} day"
            else:
                day_logic = ""

            countdown_str = f"{hours:02}:{minutes:02}:{seconds:02}"
            countdown_str = countdown_str.split('.')[0]

            if version == 1:
                main_formatted_str = f"{self.name}\n{self.vehicle}\n{self.lc}\n{self.country}"
            elif version == 2:
                main_formatted_str = f"{self.name}\n{self.vehicle}\n{self.lc}\n{self.country}"

            countdown_formatted_str = f"{day_logic}\n{countdown_str}"
            # print(f"\r{name} - {vehicle} - {provider} - {pad} - {countdown_str}", end="") <-- For debugging screen errors

            self.countdown_text_area.text = countdown_formatted_str
            self.main_text_area.text = main_formatted_str

            self.counter += 1
            if self.counter == 1:
                print("Countdown active")

            sleep(display_interval)


if __name__ == "__main__":
    control = PicoControl()
    control.led_toggle(False)
    control.visuals("FB6CFB")
    control.wifi_connect()

    while True:
        control.get_launch_info()
        control.json_error_handling()
        control.countdown_loop(120, 0.1, 1)

        control.countdown_text_area.text = ""
        control.main_text_area.text = "\n\n\nRefreshing..."

