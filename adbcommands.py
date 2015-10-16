"""
Collection of methods needed for interacting with the avd or adb
"""

import subprocess
import time
import os
import shlex
import shutil

def restart_machine(name, filedir):
	stop_avd()
	start_avd(name, filedir)				

def start_avd(name, filedir, newavddir):
	p = subprocess.Popen(["emulator", "-avd", name, "-sdcard", newavddir + "/sdcard.img", "-kernel", filedir + "/gKernel3.4", "-show-kernel", "-verbose"], cwd = r'/usr/share/android-sdk/sdk')
			
def stop_avd():
	subprocess.call(['killall', '-9', 'emulator64-arm'])

def check_sd_size(avdpath, supposedsize):
	sdpath = avdpath + '/sdcard.img'
	err_counter = 0
	try:
		currentsdsize = os.path.getsize(sdpath) >>20
	except:
		pass
	while currentsdsize < supposedsize:
		if err_counter > 20:
			raise Exception ("Error: sdcard coult not not be created. Is the HD busy?")
		print "not yet"
		err_counter += 1
		time.sleep(1.0)
	

def kill_blocking_processes():
	#SIGTERM
	subprocess.call(['pkill', '-x', 'adb'])
	print "checking if abd-processes are running"
	p = subprocess.Popen(['pgrep', '-c', 'adb'], stdout=subprocess.PIPE)
	out = 	p.communicate()[0]
	for line in out:
		if len(line.strip()) != 0 :
			padb = line
	if padb != 0:
		#SIGKILL
		print "killing adb-processes"
		subprocess.call(['killall', '-9', 'adb'])

def kill_adb_by_name(avdname):
	subprocess.call(['adb', '-s', avdname, 'emu', 'kill']) 

def get_emulator_pid():
	p = subprocess.Popen(['pgrep', 'emulator64-arm'], stdout=subprocess.PIPE)
	out = 	p.communicate()[0]
	for line in out.split('\n'):
		if len(line.strip()) != 0 :
			padb = line
			return padb

def other_emulator_online():
	avdname = ""
	status = ""
	p = subprocess.Popen(['adb', 'devices'], stdout=subprocess.PIPE)
	out = p.communicate()[0]
	for line in out.split('\n'):
		if len(line) != 0:
			if (line[0] != '*') and( not line[0].isspace()) and  ('List of devices' not in line):
				tmplist = line.split()
				if tmplist[1] == 'offline':
					raise NotImplementedError("An emulator is offline. Please terminate the offline-emulator and start the script again.")
				if avdname != "":
					raise NotImplementedError("Running multiple emulators is not supported in this version.")
				avdname = tmplist[0]
				avdstatus = tmplist[1]
				break
	if avdname != "":
		print "emulator '" + avdname + "' running. It will be used for periodic ram-dumps. Please open the apk that you want to examine manually. Please be aware that using running emulators is not fully supported"
		time.sleep(5.0)
		return True
	return False



def install_lime(filedir):
	print "installing lime"
	cmd = "adb push {} /sdcard/lime.ko".format(filedir + '/lime-goldfish.ko')
	p = subprocess.Popen(shlex.split(cmd), stdout=subprocess.PIPE)
	p.communicate()


def copy_from_tmp(outputpath, tmpfilepath, filename):
	try:
		shutil.move(tmpfilepath, outputpath + '/' + filename)
	except Exception as e:
		print "Error - could not copy dump from tmp-folder. " + str(e)
