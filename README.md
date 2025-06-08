# PicoLaunchTimer
![GitHub Release](https://img.shields.io/github/v/release/gsl4295/PicoLaunchTimer?include_prereleases&sort=date&display_name=tag)
![GitHub commit activity](https://img.shields.io/github/commit-activity/t/gsl4295/PicoLaunchTimer)
![GitHub Issues or Pull Requests](https://img.shields.io/github/issues/gsl4295/PicoLaunchTimer)<br>
A CircuitPython-based microcontroller dedicated to showing a live countdown to the next orbital rocket launch.

### Hardware
- The pin diagram for my screen specifically is located in `/info/pin-info.md`.
- A top-down view of my setup is in `/info/pico-top-down-view.jpg`
- I used a [Raspberry Pi WH](https://www.amazon.com/Raspberry-Pi-RP-PICO-WH-Pico-WH/dp/B0C58X9Q77) (wifi enabled, headers attached)
- The exact screen I used is a 1.8" 128x160 SPI TFT display. Find it [here on Amazon](https://a.co/d/0OCU4uG).

### Installation & Setup
- I have some pictures of my setup available in this repo, but you can use pin-info.txt as a resource too.
- This is coded in circuitpython-9.X. Download the latest version [here](https://circuitpython.org/board/raspberry_pi_pico_w/).
- I use Thonny for my microcontrollers but I'm sure there are alternatives.
  - In Thonny you can download Circuitpython onto the Pico easily through the Interpreter tab of the Options menu.
  - Just make sure to press the 'bootsel' button on the Pico the first time you plug it in.
- It also uses adafruit's [extra libraries package](https://circuitpython.org/libraries). Make sure to grab a version that is compatible with 9.X '.mpy' file types (it seems like 10.X will also work).
  - From this package, it is necessary to copy and paste the following files or folders over to your pico's /lib directory.
    - adafruit_display_text
    - adafruit_datetime
    - adafruit_requests
    - adafruit_st7735r
    - adafruit_connection_manager
    - adafruit_ticks
- Use environment variables for internet connectivity through CircuitPython's built-in `settings.toml` file. 
  - Set "WIFI" and "PASS" to strings of your SSID and password. The whole file should look like this:<br>
```toml
WIFI = "placeholder"
PASS = "placeholder"
```
- Then just run the code. I left a few options that I'll go over in the Features section, but
  it should be a fairly simple installation process.

### Features
- *Manual countdown data*
  - Toggles the screen between the next orbital rocket and a hardcoded date & time input from the user.
  - This feature can be toggled with a button. More details are located in `pin-info.md`
- *Functional GUI*
  - One of the main goals I had with this project was to make clean, modular graphics on the display.
  - The `adafruit_display_text` library is simply amazing for this purpose, as you'll especially see from the scrolling text.
- *[RocketLaunch.Live](https://rocketlaunch.live) integration*
  - This code partially relies on data from [the rocketlaunch.live API](https://rocketlaunch.live/api).
  - It's like the Wikipedia of launch tracking - anyone can contribute.
  - Plus, more contributions will only make this code more reliable!
- *Automatic DST Conversion*
  - It calls [timeapi.io](https://timeapi.io) in order to update the daylight savings time calculations at startup only.

### Future Additions
- I want to make this timer even more functional at some point, which definitely includes adding a simple clock function.
  - This would drastically strip down the code, not needing all the launch data that I manage here.
- Unit testing
  - Sidenote: this would be the first project that I actually add that to. Fun!
- Better error handling
  - Right now my code just wings it, and if the API doesn't give it the things that it wants, it will crash out.
  - Maybe a better term for this would be "anger management" in that case

### Footnotes
Thank you for reading! More to come.