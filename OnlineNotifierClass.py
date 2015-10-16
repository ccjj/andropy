"""
Starts the avd, checks if the avd takes too long to boot and restarts, checks if the avd is ready by requesting sys.boot_completed from the adb shell.
"""
import subprocess
import threading
import time
import adbcommands

class OnlineNotifier(object):
	timer = 0
	err_counter = 0

	def __init__(self, name, filedir, newavddir):
		self.name = name
		self.filedir = filedir
		self.timeout = 1200
		self.newavddir = newavddir

	def online_check(self):
		sflag = False
		bootcompleted = subprocess.Popen(['adb', 'shell', 'getprop', 'sys.boot_completed'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
		out, err = bootcompleted.communicate()
		for line in out.split('\n'):
			if line.strip() == "1":
				sflag = True

		for line in err:#supress device error - offline warning whenever calling
			pass
		if sflag == False:
			print "android booting since %i seconds, please wait" %self.timer
			return False
		else:
			print "android booted successfully"
			return True		
	
	"""signal that shell is available, or the timeout exceeded"""
	def check_daemon(self):
		stopFlag = False
		while stopFlag == False:
			if self.online_check() is True:
				break
			if self.timer > self.timeout:
				break
						
			self.timer += 6
			time.sleep(6)
			

	def restart_machine(self):
		adbcommands.stop_avd()
		self.err_counter += 1
		self.timer = 0
		print "restarted " + str(self.err_counter) + " times"

		self.start_machine()	


	def start_machine(self):
		if self.err_counter >= 4:
			raise Exception('Critical error: could not start the android emulator')
		daemonthread = threading.Thread(target=self.check_daemon)
		daemonthread.start()
		print "daemon started"
		adbcommands.start_avd(self.name, self.filedir, self.newavddir)
		daemonthread.join()
		if self.timer > self.timeout:
			print "restarting avd - timeout exceeded"
			self.restart_machine()
