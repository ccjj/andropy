class Config:

	#virus and machinename are the same!
	def __init__(self, samplepath, interval, sdcard=False, outputpath=False, customconfig=False):
		self.samplepath = samplepath #path of the malware sample
		self.name = os.path.splitext(os.path.basename(samplepath))[0] #name of the file without extension will be used as avdname
		self.interval = interval #how often dumps should be taken
		self.avddir = '/home/{}/.android/avd'.format(self.get_username())	

		if sdcard is not None:
			self.avdini = 'config_sd.ini'
			self.sdcard = sdcard
		else:
			self.avdini = 'config_nosd.ini'
			self.sdcard = 30
		self.selfdir = os.path.dirname(os.path.abspath(__file__)) #path of the analyzing-script, pre-defined
		if outputpath is None or outputpath == False:
			self.outputpath = self.selfdir
		else:
			self.outputpath = outputpath #custom dump-outputpath TODO
		self.customconfig = customconfig #custom avd hardwareconfig
		self.filedir = self.selfdir + '/files' #path of lime.ko and kernel
		self.configdir= self.selfdir + '/configs' #path of preconfigured avd-configs, pre-defined
		self.newavddir = self.avddir + '/' + self.name + '.avd' #folder of the new avd machine
	
	def set_apk_infos(self, package, activity):
		self.package = package
		self.activity = activity

	def get_username(self):
		return pwd.getpwuid(os.getuid()).pw_name

import os
import pwd
