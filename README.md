# RavenWatch
Free video surveillance software system with next-generation features like facial recognition, weapons detection, improved motion detection and rtsp support.

![ravenwatch free surveillance software system](https://jamesburnett.io/wp-content/uploads/2020/01/ravenwatch-1.jpg)


More at https://jamesburnett.io

Email: james@jamesburnett.io


## Features:

- Real-time Alerting.

- HTML5 Responsive, Mobile first user interface.

- Supports unlimited cameras limited only by server power.

- Supports all cameras that support and follow RTSP standards. 


## Coming Soon:

- Improved motion detection.

- Human and facial detection.

- Weapons and gun detection.



## Requirements
  - Linux, Windows or Mac OSX that supports Python 3.5.x - 3.7.x
  - *Optional - NVidia CUDA 10 installed with driver for Xorg
  - *Optional - cudNN 7.3 for CUDA 10 support 
  - *Optional - dlib 19.16
  
 
## Usage:

- Make a copy of the config.conf file and configure your cameras.

- Start the service by running the ravenwatch.py program 
  <pre>$ python3.5 ~/ravenwatch.py /path/to/config.conf file.</pre>

- Point your browser to the server where ravenwatch.py is running.
  <pre>http://127.0.0.1:8080/cams.html</pre>

## Installation

See: https://jamesburnett.io/
