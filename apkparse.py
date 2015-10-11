import subprocess
import threading
import time
import datetime
import re
import os

#example:
#package: name='h.w' versionCode='1' versionName='a'
#launchable-activity: name='a.a'  label='' icon=''


def get_package_infos(samplepath):
	cmd = 'aapt dump badging {} | grep "package\|activity"'.format(samplepath)
	try:
		out = subprocess.Popen(['/bin/bash', '-c', cmd], stdout=subprocess.PIPE)
		for line in out.stdout:
			if "package" in line:
				s = line.lstrip("package: name=")[1:]
				t = s.find ("' versionCode='")
				s = s[:t]
				package = s
			elif "activity" in line:
				s = line.lstrip("launchable-activity: name=")[1:]
				t = s.find ("'  label='")
				s = s[:t]
				activity = s
		print "p: " + package + "\na:" + activity
		if activity is None or package is None:
			print "Error parsing apk - please start the apk when the machine is fully bootet"
			return False, False
		return package, activity
	except Exception, e:
		print "Error parsing apk - please start the apk when the machine is fully bootet"
		return False, False
		#def parse_apk(samplepath):	
	
#pkg, act = get_package_infos("/home/santoku4/Desktop/pyscripts/smallest.apk")

#raw_input("push [Enter] if you have started the app")
#subprocess.call(['adb', 'shell', 'monkey', '-p', pkg, '-c', 'android.intent.category.LAUNCHER', '1'])

