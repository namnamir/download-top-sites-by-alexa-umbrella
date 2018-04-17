# Download Top 1 Million Alexa Sites
This piece of code downloads the list of the top 1M Alexa or Umbrella websites and download them on the local machine.

## How to use

* Run this code on a (Debian-based) Linux distro.

* *unzip* package needs to be installed.

`sudo apt-get install unzip`

* When the coded is run there are the following options:


| Option | Description |
| --- | --- |
| "-a" or "--alexa" | Get list of the domains from Alexa and unzip it |
| "-c" or "--cisco" | Get list of the domains from [Cisco Umbrella](http://s3-us-west-1.amazonaws.com/umbrella-static/index.html) and unzip it |
| "-s", "--statvoo" | Get list of the domains from [Statvoo](https://siteinfo.statvoo.com/top/sites) and unzip it. It is the alternative Alexa list in case of any issue with Alexa website. |
| "-F", "--file" | Path to the file containing the list of domains and ranksin format xxx,yyy for each row (e.g. 1,google.com); default is *top.csv* in the root folder |
| "-S", "--show" | Turn on/off the showing output on the screen; it needs to be like  `python3 main.py --show 0` which means "don't show the activities"|
