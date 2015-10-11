import argparser
import sys
import ConfigClass
import createfiles
import OnlineNotifierClass
import machineClass
import apkparse
import subprocess
import time
import thread
import threading
import adbcommands

def create_and_config(a, b, c ,d, e, isrunning):	
	config = ConfigClass.Config(a, b, c, d, e)
	createfiles.create_avd_files(config.name, config.avddir, config.configdir, config.newavddir, config.outputpath, config.avdini, config.sdcard, isrunning)
	f, g = apkparse.get_package_infos(config.samplepath)
	config.set_apk_infos(f, g)
	return config

def main(argv):
	#inserts in the config-constructor args.samplepath, args.interval, args.sdcard, args.outputpath, args.customconfig
	a, b, c, d, e = argparser.get_args()
	adbcommands.kill_blocking_processes()
	
	if adbcommands.check_online_devices() == False: #no other device running
		config = create_and_config(a, b, c ,d, e, False)
		machine = OnlineNotifierClass.OnlineNotifier(config.name, config.filedir)
		machine.start_machine()
	else: #some other device is running
		config = create_and_config(a, b, c ,d, e, True)
	start_online_timer()
	android = machineClass.Device(config)
	android.start()



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
