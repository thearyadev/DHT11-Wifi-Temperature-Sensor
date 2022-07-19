# Raspberry Pi Pico W Temperature sensor.

`web_server` contains the flask web server to receive and display data on the webpage.

Configure this by modifying `credentials.py` in the root directory. 

`main.py` In the root directory is the MicroPython script for the microcontroller. This file will need to be configured to include the GPIO pin number for the DHT11 as well as any indicator LED's. 
Flash `main.py` and `credentials.py` to the microcontroller.

`/web-server/main.py` is the flask web server. This will contain the databases & user interface for this project. 