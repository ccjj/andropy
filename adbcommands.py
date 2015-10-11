import subprocess
import time


def restart_machine(name, filedir):
	stop_avd()
	start_avd(name, filedir)				

def start_avd(name, filedir):
	subprocess.Popen(["emulator", "-avd", name, "-kernel", filedir + "/gKernel3.4", "-verbose"], cwd = r'/usr/share/android-sdk/sdk')
			
def stop_avd():
	subprocess.call(['killall', '-9', 'emulator64-arm'])


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




def check_online_devices():
	avdname = ""
	status = ""
	p = subprocess.Popen(['adb', 'devices'], stdout=subprocess.PIPE)
	out = p.communicate()[0]
	for line in out.split('\n'):
		if len(line) != 0:
			if (line[0] != '*') and( not line[0].isspace()) and  ('List of devices' not in line):
				tmplist = line.split()
				avdname = tmplist[0]
				avdstatus = tmplist[1]
				#print "avd" +  avdname
				#print "stat" + avdstatus
				break
	if avdname != "" and avdstatus != 'offline':
		print "emulator '" + avdname + "' running. It will be used for periodic ram-dumps. Please open the apk that you want to examine manually. Please be aware that using running emulators is not fully supported"
		time.sleep(5.0)
		return True
	return False
