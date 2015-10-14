import subprocess
import threading
import time
import datetime
import re
import os
import shutil
import shlex

class Device:
	oflag = False  # is there any io operation in progress?

	def __init__(self, config):
		self.filedir = config.filedir
		self.samplepath = config.samplepath
		self.package = config.package
		self.activity = config.activity
		self.sdcard = config.sdcard
		self.name = config.name
		self.outputpath = config.outputpath
		self.interval = config.interval
		self.newavddir = config.newavddir
		self.avdpid = config.avdpid

	def start(self):
		adbcommands.install_lime()
		self.install_apk()
		self.start_apk()
		self.remove_lime() 
		self.copy_dump(True)

	def install_apk(self):
		subprocess.call(['adb', 'install', self.samplepath])

	def restart_adb(self):
		print "restarting adb"
		p = subprocess.call(['adb', 'kill-server'])
		subprocess.call(['pkill', '-x', 'adb'])
		subprocess.call(['adb', 'start-server'])
		time.sleep(10.0)

	def remove_lime(self):
		cmd = "adb shell rmmod lime"
		p = subprocess.Popen(cmd.split())
		output = p.communicate()[0]


	def get_dump_from_sd(self, name):
		# gets the node-number of lime.dump on the sd-card
		node = ""
		getnodecmd = "fls -r -p {}".format(self.newavddir + '/sdcard.img')
		p = subprocess.Popen(shlex.split(getnodecmd), stdout=subprocess.PIPE)
		output = p.communicate()[0]
		for line in output.split('\n'):
			if 'lime.dump' in line:
				node = re.search(r"([0-9]+)", line).group(1)
		if node == "":
			print "Error - could not locate dump on sdcard"
			return False
		rtnfls = p.returncode
		if rtnfls != 0:
			return False
		# extracts node
		icatcmd = "icat {} {} > {}".format(self.newavddir + '/sdcard.img', node, self.outputpath)
		extractnode = subprocess.Popen(icatcmd, shell=True)
		rtncat = extractnode.returncode
		if rtncat != 0:
			return False
		return True

	def send_broadcast(self):
		p = subprocess.Popen(["adb", "shell", "insmod", "/sdcard/lime.ko", "path=tcp:4444 format=lime"])



	def tcp_get_output(self, outputname, send_result):
		Psuccess = False
		err_counter = 0

		while Psuccess == False:
			if err_counter > 6:
				break
			Psuccess = self.check_success_ncat(outputname)
			err_counter += 1
			time.sleep(2.0)
		send_result.append(Psuccess)


	def check_success_ncat(self, outputname):
		if not os.path.isfile(outputname) or (os.path.getsize(outputname) == 0):
			self.cbroadcast(outputname)
			return False
		else:
			return True


	def cbroadcast(self, outputname):
		cmd = 'nc localhost 4444 | pv -e -b > "{}"'.format(outputname)
		recievetcp = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
		recievetcp.communicate()

	def copy_dump(self, firstcall):
		if firstcall == False:
			self.remove_lime()
		if self.sdcard > 31:  # case sd
			self.get_over_sd()
		else:  # case tcp
			if firstcall == True:
				opentcp = subprocess.check_output(["adb", "forward", "tcp:4444", "tcp:4444"])
			self.get_over_tcp()


	def create_filename(self, outputpath, name):
		now = datetime.datetime.now().strftime("%y-%m-%d-%H:%M:%S")
		filename = 'lime-' + name + '-' + now + '.dump'
		tmpfilepath = outputpath + '/tmp/' + filename
		return filename, tmpfilepath


	def get_over_sd(self):  # todo rename outputname, create constructor with config
		#if adbcommands.is_emulator_alive(self.avdpid) != True:
		#	return
		threading.Timer(self.interval, self.get_over_sd).start()
		if self.check_oflag() == True:
			print "copy-dump-operation from sd skipped because there was an other operation in progress"
			return
		outputname, tmpfilepath = self.create_filename(self.outputpath, self.name)
		self.oflag = True
		print "Attempting to dump the RAM to sdcard"
		cmd = 'adb shell insmod /sdcard/lime.ko path=/sdcard/lime.dump format=lime'
		s = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
		s.communicate()
		if self.get_dump_from_sd(outputname) == True:

			print "Successfully aquired ram-dump over SD"
		else:
			print "Error - could not dump the ram over SD"
		self.remove_lime()
		self.oflag = False


	def get_over_tcp(self):
		#if adbcommands.is_emulator_alive(self.avdpid) != True:
		#	return
		threading.Timer(self.interval, self.get_over_tcp).start()
		if self.check_oflag() == True:
			print "copy-dump-operation from tcp skipped because there was an other operation in progress"
			return
		filename, tmpfilepath = self.create_filename(self.outputpath, self.name)
		s = threading.Thread(target=self.send_broadcast)
		send_result = []
		t = threading.Timer(3.5, self.tcp_get_output, args=(tmpfilepath, send_result))
		self.oflag = True
		s.start()
		print "start receiving"
		t.start()
		t.join()
		if send_result[0] == True:
			adbcommands.copy_from_tmp(self.outputpath, tmpfilepath, filename)
			print "Successfully received tcp-dump"
		else:
			print "Error - could not get data from tcp. Maybe the kernel is busy?"
			try:
				os.remove(tmpfilepath)
			except:
				pass
		self.remove_lime()
		self.oflag = False


	def check_oflag(self):
		err_counter = 0
		while self.oflag == True:
			time.sleep(1.0)
			err_counter += 1
			if err_counter > 10:
				return True
		return False

	
	def start_apk(self):
		print "attempting to install the apk"
		if self.package != False and self.package is not None:
			subprocess.call(['adb', 'shell', 'monkey', '-p', self.package, '-c', 'android.intent.category.LAUNCHER', '1'])
		else:
			print("Error parsing apk - please start the app manually, then continue the app\n")
			raw_input("push [Enter] if you have started the app")

