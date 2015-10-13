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

	def start(self):
		# print config.filedir
		self.install_lime(self.filedir)
		self.installapk(self.samplepath)
		self.start_apk(self.package, self.activity)
		self.remove_lime()  # TODO only for debug
		self.copydump(self.name, self.sdcard, self.outputpath, self.interval, self.newavddir, True)

	def installapk(self, samplepath):
		subprocess.check_call(['adb', 'install', samplepath], stdout=subprocess.PIPE)

	def restart_adb(self):
		print "restarting adb"
		p = subprocess.call(['adb', 'kill-server'])
		subprocess.call(['pkill', '-x', 'adb'])
		subprocess.call(['adb', 'start-server'])
		time.sleep(10.0)

	def remove_lime(self, err_counter=0):
		cmd = "adb shell rmmod lime"
		p = subprocess.Popen(cmd.split(), stdout=subprocess.PIPE)
		output = p.communicate()[0]


	def get_dump_from_sd(self, name, outputpath, newavddir):
		# gets the node-number of lime.dump on the sd-card
		node = ""
		cmd = "fls -r -p {}".format(newavddir + '/sdcard.img')
		ps = subprocess.Popen(shlex.split(cmd), stdout=subprocess.PIPE)
		output = ps.communicate()[0]
		for line in output.split('\n'):
			if 'lime.dump' in line:
				node = re.search(r"([0-9]+)", line).group(1)
		if node == "":
			print "Error - could not locate dump on sdcard"
			return False
		# extracts node
		cmd2 = "icat {} {} > {}".format(newavddir + '/sdcard.img', node, outputpath)
		extractnode = subprocess.call(['/bin/bash', '-c', cmd2])

	def sendbroadcast(self):
		p = subprocess.Popen(["adb", "shell", "insmod", "/sdcard/lime.ko", "path=tcp:4444 format=lime"])



	def tcp_get_output(self, outputname, send_result):
		Psuccess = False
		err_counter = 0

		while Psuccess == False:
			if err_counter > 6:
				break
			send_result
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
		command = 'nc localhost 4444 | pv -e -b > "{}"'.format(outputname)
		# wait for the process to finish with check call
		recievetcp = subprocess.Popen(['/bin/bash', '-c', command], stdout=subprocess.PIPE)
		for line in recievetcp.stdout:
			print line


	def copydump(self, name, sdcard, outputpath, interval, newavddir, firstcall):
		if firstcall == False:
			self.remove_lime()
		if sdcard:  # case sd TODO change param order
			self.get_over_sd(interval, outputpath, name, newavddir)
		else:  # case tcp
			if firstcall == True:
				opentcp = subprocess.check_output(["adb", "forward", "tcp:4444", "tcp:4444"])
			self.get_over_tcp(interval, outputpath, name)


	def create_filename(self, name, outputpath):
		now = datetime.datetime.now().strftime("%y-%m-%d-%H:%M:%S")
		filename = 'lime-' + name + '-' + now + '.dump'  # NEW
		tmpfilepath = outputpath + '/tmp/' + filename  # NEW
		return filename, tmpfilepath


	def get_over_sd(self, interval, outputpath, name, newavddir):  # todo rename outputname, create constructor with config
		threading.Timer(interval, self.get_over_sd, args=(interval, name, outputpath, newavddir)).start()
		if self.check_oflag() == True:
			print "copy-dump-operation from sd skipped because there was an other operation in progress"
			return
		filename, tmpfilepath = self.create_filename(name, str(outputpath))
		self.oflag = True
		print "Attempting to dump the RAM to sdcard"
		copysd = subprocess.call(['adb', 'shell', 'insmod', '/sdcard/lime.ko', 'path=/sdcard/lime.dump format=lime'])
		self.get_dump_from_sd(name, tmpfilepath, newavddir)
		print "SUCCESS"
		self.copy_from_tmp(outputpath, tmpfilepath, filename)
		self.remove_lime()
		self.oflag = False


	def get_over_tcp(self, interval, outputpath, name):
		threading.Timer(interval, self.get_over_tcp, args=(interval, outputpath, name)).start()
		if self.check_oflag() == True:
			print "copy-dump-operation from tcp skipped because there was an other operation in progress"
			return
		filename, tmpfilepath = self.create_filename(name, outputpath)
		s = threading.Thread(target=self.sendbroadcast)
		send_result = []
		t = threading.Timer(3.5, self.tcp_get_output, args=(tmpfilepath, send_result))
		self.oflag = True
		s.start()
		print "start receiving"
		t.start()
		t.join()
		if send_result[0] == True:
			print "SUCCESS"
			self.copy_from_tmp(outputpath, tmpfilepath, filename)
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


	def install_lime(self, filedir):
		print "installing lime"
		cmd = "adb push {} /sdcard/lime.ko".format(filedir + '/lime-goldfish.ko')
		p = subprocess.Popen(cmd.split(), stdout=subprocess.PIPE)
		p.communicate()
		exit_code = p.wait()
	
	def start_apk(self, package=False, activity=False):
		print "attempting to install the apk"
		if package != False and package is not None:
			subprocess.call(['adb', 'shell', 'monkey', '-p', package, '-c', 'android.intent.category.LAUNCHER', '1'])
		else:
			print("error parsing apk - please start the app manually, then continue the app")
			raw_input("push [Enter] if you have started the app")


	def copy_from_tmp(self, outputpath, outputname, filename):
		try:
			shutil.move(outputname, outputpath + '/' + filename)
		except:
			print "error - could not copy dump from tmp-folder"
			pass
