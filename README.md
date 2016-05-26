# streamerino
An application to browse and watch twitch.tv streams without a webbrowser or flash. In order to watch the streams you need livestreamer installed on your system. Livestreamer is available for multiple platforms. This application requires gtk 3.

## Installation

To run this programm, you need Python and Gtk3 installed. In order to watch the
streams in your favourite media player, you need to install livestreamer.

### Unix

First make sure you have python installed:
```
apt-get install python
´´´

The easiest way to install livestreamer is using pip. Run as root:

```
pip install livestreamer
´´´

Make sure you have Gtk3 installed:
```
apt-get install libgtk-3-0
´´´

Now clone this repository and run the programm:
```
git clone https://github.com/biberino/streamerino
cd streamerino
python streamerino.py
´´´




