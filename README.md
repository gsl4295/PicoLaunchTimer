# PicoLaunchTimer
CircuitPython-based clock dedicated to showing a live countdown to the next orbital rocket launch.

### Hardware
- The pin diagram for my screen specifically is located in pin-info.
- I used a [Raspberry Pi WH](https://www.amazon.com/Raspberry-Pi-RP-PICO-WH-Pico-WH/dp/B0C58X9Q77) (wifi enabled, headers attached)
- The exact screen I used is a 1.8" 128x160 SPI TFT display. Find it [here on Amazon](https://a.co/d/0OCU4uG).

### Installation & Setup
- I have some pictures of my setup available, but you can also use pin-info.txt as a resource.
- 
- This is coded in circuitpython-9.X. Download the latest version [here](https://circuitpython.org/board/raspberry_pi_pico_w/).
- I use Thonny for my microcontrollers but I'm sure there are alternatives.
  - In Thonny you can download Circuitpython onto the Pico easily through the Interpreter tab of the options menu.
  - Just make sure to press the bootselect button on the Pico when you plug it in.
- It also uses adafruit's [extra libraries package](https://circuitpython.org/libraries). Make sure to grab a version that is compatible with 9.X '.mpy' file types (it seems like 10.X will also work).
  - From this package it is necessary to copy and paste the following files or folders over to your pico's /lib directory.
    - adafruit_display_text
    - adafruit_datetime
    - adafruit_requests
    - adafruit_st7735r
    - adafruit_connection_manager
    - adafruit_ticks
- Use environment variables for internet connectivity through circuitpython's built-in "settings.toml" file. 
  - Set "WIFI" and "PASS" to strings of your SSID and password.
- 

