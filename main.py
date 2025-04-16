# This is code for my command-line T-0 timer that's been adapted to a Raspberry Pi Pico WH.
# It tracks the next orbital (or significant sub-orbital) launch and counts down to it.
# Info about hardware requirements for this project is located at /pin-info.txt and the readme.md.

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

print("System in startup (on internal power)")

# Turn off built-in LED
led = DigitalInOut(LED)  # Built-in LED
led.direction = Direction.OUTPUT
led.value = False

mosi_pin = GP11
clk_pin = GP10
reset_pin = GP17
cs_pin = GP18
dc_pin = GP16

print("Imported libraries and assigned pins.")

release_displays()

spi = SPI(clock=clk_pin, MOSI=mosi_pin)
display_bus = FourWire(spi, command=dc_pin, chip_select=cs_pin, reset=reset_pin)
display = ST7735R(display_bus, width=128, height=160, bgr=True)

print("Display registered.")

# Add background
splash = Group()
display.root_group = splash

color_bitmap = Bitmap(128, 160, 1)

color_palette = Palette(1)
color_palette[0] = 0xFB6CFB  # Background color

bg_sprite = TileGrid(color_bitmap, pixel_shader=color_palette, x=0, y=0)
splash.append(bg_sprite)

print("Background created.")

# Create black rectangle
# This visually makes the purple background look like just a border
inner_bitmap = Bitmap(118, 150, 1)
inner_palette = Palette(1)
inner_palette[0] = 0x000000  # Black
inner_sprite = TileGrid(inner_bitmap, pixel_shader=inner_palette, x=5, y=5)
splash.append(inner_sprite)

print("Inner rectangle created.")

# Draw "Next Spaceflight" header
header_text_group = Group(scale=1, x=16, y=18)
header_text = "Next Spaceflight"
header_text_area = label.Label(FONT, text=header_text, color=0xFB6CFB)
header_text_group.append(header_text_area)  # Subgroup for text scaling
splash.append(header_text_group)

print("Text created, picture displaying now.")
print("Attempting to connect to Wi-Fi.")

# A loop derived from myoldmopar's TemperatureSensing project. Note that this will keep trying to connect forever.
while True:
    try:
        radio.connect(getenv("WIFI"), getenv("PASS"))
        print(f"Connected to the internet.")
        break
    except ConnectionError:
        continue
    print("No connection. Trying again in 2 seconds.")
    sleep(2)

# This part is courtesy of chatgpt.
pool = socketpool.SocketPool(radio)
requests = adafruit_requests.Session(pool, ssl.create_default_context())

print("Starting countdown loop.")

countdown_text_group = Group(scale=2, x=16, y=42)
countdown_text_area = label.Label(FONT, text="", color=0xFFFFFF)
countdown_text_group.append(countdown_text_area)
splash.append(countdown_text_group)

main_text_group = Group(scale=1, x=16, y=96)
main_text_area = label.Label(FONT, text="\n\n\nLoading...", color=0xFB6CFB)
main_text_group.append(main_text_area)
splash.append(main_text_group)

while True:
    response = requests.get("https://fdo.rocketlaunch.live/json/launches/next/1")
    content = response.json()
    launch = content["result"][0]
    name = launch["name"]
    t0 = launch["t0"]
    win_open = launch["win_open"]
    win_close = launch["win_close"]
    provider = launch["provider"]["name"]
    vehicle = launch["vehicle"]["name"]
    pad = launch["pad"]["name"]
    lc = launch["pad"]["location"]["name"]
    country = launch["pad"]["location"]["country"]

    d, t = t0[:-1].split("T")
    y, m, dy = d.split("-")
    h, mi = t.split(":")
    launch_time = datetime(int(y), int(m), int(dy), int(h) - 5, int(mi))
    http_time = 120  # Seconds
    display_interval = 0.1
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
        countdown_str = str(countdown_str).split('.')[0]

        main_formatted_str = f"{name}\n{vehicle}\n{lc}\n{country}"
        countdown_formatted_str = f"{day_logic}\n{countdown_str}"
        # print(f"\r{name} - {vehicle} - {provider} - {pad} - {countdown_str}", end="") <-- For debugging screen errors

        countdown_text_area.text = countdown_formatted_str
        main_text_area.text = main_formatted_str
        sleep(display_interval)
    countdown_text_area.text = ""
    main_text_area.text = "\n\n\nRefreshing..."

while True:
    pass

