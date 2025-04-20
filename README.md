# PicoLaunchTimer
Python-based clock for tracking the current T-0 and general information about a rocket launch.
Partially adapted by code from [myoldmopar's repo](https://github.com/okielife/TemperatureSensing).

### Hardware
- The pin diagram for my screen specifically is located in pin-info.
- I used a Raspberry Pi WH (wifi enabled, headers attached)
  - Can be bought on amazon for fairly cheap. MSRP is around $5-10 if I remember correctly
- Screen is a 1.8" SPI with 128x160 pixels.
- I also used a fairly large breadboard for my personal build, but anything is obviously fine

### Software
- This is coded in circuitpython-9.X. Download the latest version [here](https://circuitpython.org/board/raspberry_pi_pico_w/).
- I use Thonny for my microcontrollers but I'm sure there are alternatives.
  - In Thonny you can download Circuitpython onto the Pico easily through the Interpreter tab of the options menu.
  - Just make sure to press the bootselect button on the Pico when you plug it in.
- It also uses adafruit's [extra libraries package](https://circuitpython.org/libraries). Make sure to grab a version that is compatible with 9.X .mpy file types (it seems like 10.X would also work).
  - From this package you need to copy and paste the following files or folders over to your pico's lib folder.
    - adafruit_display_text
    - adafruit_datetime
    - adafruit_requests
    - adafruit_st7735r
- Use environment variables for internet connectivity through circuitpython's built-in "settings.toml" file. 
  - Set "WIFI" and "PASS" equal to a string of your SSID and password.

### Other Info
- It uses the API from [rocketlaunch.live](https://rocketlaunch.live), which isn't ideal due to the lack of updates on their website. I'll try and use [nextspaceflight.com](https://nextspaceflight.com) at some point.