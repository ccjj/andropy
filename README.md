# andropy
Helps automating creating lime-dumps

It basically creates a new avd, starts the avd, and creates ram-dumps with the lime-kernel-module periodically, over tcp or over sd card.

The dumps can be later processed with volatility, an easy-to-use-program is attached.

Commands for andropy, the main-tool:

usage: androstart.py [-h] -n SAMPLEPATH -i INTERVAL [-d SDCARD] [-o OUTPUTPATH]
                   [-c CUSTOMCONFIG]

Automates android memory dumping. Creates an avd and dumps the ram with the LIME module regulary

optional arguments:
  -h, --help            show this help message and exit
  -n SAMPLEPATH, --samplepath SAMPLEPATH
                        path of the malware sample-apk
  -i INTERVAL, --interval INTERVAL
                        intervals for each memory dump in seconds
  -d SDCARD, --sdcard SDCARD
                        dump will be saved on the sdcard of the android device
                        instead of being transfered over TCP
  -o OUTPUTPATH, --outputpath OUTPUTPATH
                        path of the output-path
  -c CUSTOMCONFIG, --customconfig CUSTOMCONFIG
                        path of a custom avd config.ini


#Voltool
helps processing lime-dumps

The terminal-like volatility-script can run any command from volatility , and bash afterwards. 

It can:
do -one, or -all, for running a volatility command on files in a directory. -w, if one wants a textfile-output instead showing it in the console. One could also run a bash-command after -one/-all, if the command before is a valid volatility-command.
For example:

-one -f lime-smallest-15-10-07-04:11:25.dump -w linux_pslist | grep 3115

outputs in linux_pslist-smallest-15-10-07-04:11:25.txt:

0xc0f5c400 insmod               3115            0              0      0x00c44000 2015-10-07 02:11:28 UTC+0000


Dependencies:

Pipe Viewer (for checking the progress over tcp)
http://linux.die.net/man/1/pv

Android SDK
	-Android 6.0 SDK Platform (API 23)
	-ARM-eabi v7a System image
