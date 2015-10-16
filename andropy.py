"""
Starts the andropy-script, with an input to cancel it. Expects and requires the same args as the andropy-script.

After andropy finished, the volprog - tool for volatility - will be opened
"""
import argparser
import sys
import ConfigClass
import createfiles
import OnlineNotifierClass
import MachineClass
import apkparse
import subprocess
import time
import thread
import threading
import adbcommands

def create_and_config(samplepath, interval, sdcard, outputpath, False, isrunning):	
	config = ConfigClass.Config(samplepath, interval, sdcard, outputpath, False)
	createfiles.create_avd_files(config.name, config.avddir, config.configdir, config.newavddir, config.outputpath, config.avdini, config.sdcard, isrunning)
	pkg, actvt = apkparse.get_package_infos(config.samplepath)
	config.set_apk_infos(pkg, actvt)
	return config

def main(argv):
	#inserts in the config-constructor args.samplepath, args.interval, args.sdcard, args.outputpath, args.customconfig
	samplepath, interval, sdcard, outputpath, customconfig = argparser.get_args()#todo
	adbcommands.kill_blocking_processes()
	
	if adbcommands.other_emulator_online() == False: #no other device running
		config = create_and_config(samplepath, interval, sdcard, outputpath, False, False)
		machine = OnlineNotifierClass.OnlineNotifier(config.name, config.filedir, config.newavddir)
		machine.start_machine()
	else: #some other device is running
		config = create_and_config(samplepath, interval, sdcard, outputpath, False, True)
	start_online_timer()
	android = MachineClass.Device(config)
	android.start_dumping_process()



def start_online_timer():
	s = threading.Thread(target=timer_count).start()

def timer_count():
	ti = 0
	while True:
		print "AVD running since " + str(ti/60) + " minutes"
		ti += 60
		time.sleep(60.0)



if __name__ == '__main__':
    main(sys.argv[1:])
