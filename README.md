# streamerino
An application to browse and watch twitch.tv streams without a webbrowser or flash. In order to watch the streams you need livestreamer installed on your system. Livestreamer is available for multiple platforms. This application requires gtk 3.

## Installation

To run this programm, you need Python and Gtk3 installed. In order to watch the
streams in your favourite media player, you need to install livestreamer.

### Unix

First make sure you have python installed:
```
apt-get install python
```

The easiest way to install livestreamer is using your distro's repo. For Debian you type:

```
apt-get install livestreamer
```

For a full installation guide goto:
[livestreamer](http://docs.livestreamer.io/install.html)


Make sure you have Gtk3 installed:
```
apt-get install libgtk-3-0
```


Now clone this repository and run the programm:
```
git clone https://github.com/biberino/streamerino
cd streamerino
python streamerino.py
```


### Windows

This programm has only be tested on unix so far. However, it should be possible
to run this programm on windows without any issues. Follow these links to
install the needed software and then clone the repository:


[Python](https://www.python.org/downloads/windows/)<br>
[Livestreamer](http://docs.livestreamer.io/install.html)<br>

## Feedback
I would be happy to receive feedback. Please consider writing an email to
john.smithh@gmx.de




