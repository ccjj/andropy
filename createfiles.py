"""
This module creates all needed files in the avd-folder:
config.ini, copied from this scripts root path
creates a sd-card with specified size
"""
import cfgtemplate
import subprocess
import os
import errno
import shlex
from shutil import copyfile
import time
import adbcommands

""" a helper function for writing the cfgtemplate """
def write_file(content, fpath):
	f = open(fpath, "w")
	f.write(content)
	f.close()

def mkdir_abs_path(path):
	try:
		os.makedirs(path)
	except OSError as exc:
		if exc.errno == errno.EEXIST and os.path.isdir(path):
			pass
		else: raise

def create_avd_files(name, avddir, configdir, newavddir, outputpath, avdini, sdsize, isrunning=False):
	mkdir_abs_path(outputpath + '/tmp')
	print "Other avd is running: " + str(isrunning)
	avdtemplate = cfgtemplate.template(name, avddir)
	if isrunning == False:
		mkdir_abs_path(newavddir)
		sdcmd = 'mksdcard {} {}'.format(str(sdsize) + 'M', newavddir+ '/sdcard.img')
		subprocess.call(shlex.split(sdcmd))
		adbcommands.check_sd_size(newavddir, sdsize)
		print "sd created, size: " + str(sdsize)
		time.sleep(2.0)
		avdcreatecommand = 'android create avd -n {0} -t 1'.format(name)
		s1 = subprocess.Popen(avdcreatecommand.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)		
		s1.communicate('no')
		copyfile(configdir + '/' + avdini, newavddir + '/config.ini')
		write_file(avdtemplate, avddir + '/' +  name + '.ini')
