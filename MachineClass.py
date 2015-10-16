"""
Loads the config, installs lime, starts dumping over tcp or sdcard and later removes the lime-module, before dumping again. Does install and start the apk before.
"""
import subprocess
import threading
import time
import datetime
import re
import os
import shutil
import shlex
import adbcommands

class Device(object):
	""" is True when an io operation is in progress"""
	oflag = False

	def __init__(self, config):
		self.filedir = config.filedir
		self.samplepath = config.samplepath
		self.package = config.package
		#self.activity = config.activity
		self.sdcard = config.sdcard
		self.name = config.name
		self.outputpath = config.outputpath
		self.interval = config.interval
		self.newavddir = config.newavddir
		#self.avdpid = config.avdpid

	def start_dumping_process(self):
		adbcommands.install_lime(self.filedir)
		self.install_apk()
		self.start_apk()
		time.sleep(10.0)
		self.remove_lime()# in case machine was already running
		self.copy_dump(True)

	def install_apk(self):
		subprocess.call(['adb', 'install', self.samplepath])

	def remove_lime(self):
		cmd = "adb shell rmmod lime"
		subprocess.call(cmd.split())

	def get_dump_from_sd(self, filepath):
		node = self.sd_find_node()
		if node == False:
			return False
		self.sd_extract_dump(node, filepath)
		return True

	"""extracts the dump from sd, starting from the specified sdcard-node"""
	def sd_extract_dump(self, node, filepath):
		icatcmd = "icat {} {} > {}".format(self.newavddir + '/sdcard.img', str(node), filepath)
		subprocess.call(['/bin/bash', '-c', icatcmd])

	# gets the node-number of the ram lime.dump on the sd-card
	def sd_find_node(self):
		node = ""
		getnodecmd = "fls -r -p {}".format(self.newavddir + '/sdcard.img')
		p = subprocess.Popen(getnodecmd.split(), stdout = subprocess.PIPE)
		out = p.communicate()[0]
		for line in out.split('\n'):
			if 'lime.dump' in line:
				node = re.search(r"([0-9]+)", line).group(1)
		if node == "":
			print "Error: could not locate dump on sdcard"
			print out, err
			return False
		if p.returncode != 0:
			print "Error: could not check the sdcard"
			print out, err
			return False
		return node

	def tcp_send_broadcast(self):
		p = subprocess.Popen(["adb", "shell", "insmod", "/sdcard/lime.ko", "path=tcp:4444 format=lime"])

	def tcp_get_output(self, outputname, send_result):
		Psuccess = False
		err_counter = 0
		while Psuccess == False:
			if err_counter > 6:
				break
			Psuccess = self.tcp_check_success_ncat(outputname)
			err_counter += 1
			time.sleep(2.0)
		send_result.append(Psuccess)

	def tcp_check_success_ncat(self, outputname):
		if not os.path.isfile(outputname) or (os.path.getsize(outputname) == 0):
			self.tcp_ncat_receive(outputname)
			return False
		else:
			return True


	def tcp_ncat_receive(self, outputname):
		cmd = 'nc localhost 4444 | pv -e -b > "{}"'.format(outputname)
		recievetcp = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
		recievetcp.communicate()

	def copy_dump(self, firstcall):
		if firstcall == False:
			self.remove_lime()
		if self.sdcard > 30:  # case sd
			self.get_over_sd()
		else:  # case tcp
			if firstcall == True:
				opentcp = subprocess.check_output(["adb", "forward", "tcp:4444", "tcp:4444"])
			self.get_over_tcp()


	def create_filename(self, outputpath, name):
		now = datetime.datetime.now().strftime("%m-%d-%H:%M:%S")
		filename = 'lime_' + name + '_' + now + '.dump'
		tmpfilepath = outputpath + '/tmp/' + filename
		return filename, tmpfilepath


	def get_over_sd(self):  # todo rename outputname, create constructor with config
		threading.Timer(self.interval, self.get_over_sd).start()
		if self.oflag == True:
			print "copy-dump-operation from sd skipped because there was an other operation in progress"
			return
		filename, tmpfilepath = self.create_filename(self.outputpath, self.name)
		self.oflag = True
		starttime = time.time()
		print "Attempting to dump the RAM to sdcard"
		copysd = subprocess.call(['adb', 'shell', 'insmod', '/sdcard/lime.ko', 'path=/sdcard/lime.dump format=lime'])
		if self.get_dump_from_sd(self.outputpath + '/' + filename) == True:

			print "Successfully aquired ram-dump over SD"
		else:
			print "Error - could not dump the ram over SD"
		self.remove_lime()
		elapsedtime = time.time() - starttime
		print "Dumping-operation took " + str(elapsedtime / 60 ) + " minutes"
		self.oflag = False


	def get_over_tcp(self):
		threading.Timer(self.interval, self.get_over_tcp).start()
		if self.oflag == True:
			print "copy-dump-operation from tcp skipped because there was an other operation in progress"
			return
		filename, tmpfilepath = self.create_filename(self.outputpath, self.name)
		sendtcp = threading.Thread(target=self.tcp_send_broadcast)
		send_result = []
		t = threading.Timer(3.5, self.tcp_get_output, args=(tmpfilepath, send_result))
		self.oflag = True
		starttime = time.time()
		sendtcp.start()
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
		elapsedtime = time.time() - starttime
		print "Dumping-operation took " + str(elapsedtime / 60 ) + " minutes"
		self.oflag = False

	def start_apk(self):
		print "attempting to install the apk"
		if self.package != False and self.package is not None:
			subprocess.call(['adb', 'shell', 'monkey', '-p', self.package, '-c', 'android.intent.category.LAUNCHER', '1'])
		else:
			print("Error parsing apk - please start the app manually, then continue the app\n")
			raw_input("push [Enter] if you have started the app")

