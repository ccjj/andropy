import subprocess
import threading
import time
import adbcommands



class OnlineNotifier:
	timer = 0
	err_counter = 0

	def __init__(self, name, filedir):
		self.name = name
		self.filedir = filedir
		self.timeout = 1000

	def online_check(self):
		sflag = False
		bc = subprocess.Popen(['adb', 'shell', 'getprop', 'sys.boot_completed'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
		out, err = bc.communicate()
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

	def checkDemon(self):
		stopFlag = False
		while stopFlag == False:
			if self.online_check() is True:
				break
			if self.timer > self.timeout:
				break
						
			self.timer += 6
			time.sleep(6)
			#signal that shell is available

	def restart_machine(self):
		adbcommands.stop_avd()
		self.err_counter += 1
		self.timer = 0
		print "restarted " + str(self.err_counter) + " times"

		self.start_machine()	


	def start_machine(self):
		if self.err_counter >= 4:
			raise Exception('Critical error: could not start the android emulator')
		t = threading.Thread(target=self.checkDemon)
		t.start()
		print "daemon started"
		adbcommands.start_avd(self.name, self.filedir)
		t.join()
		if self.timer > self.timeout:
			print "restarting avd - timeout exceeded"
			self.restart_machine()

