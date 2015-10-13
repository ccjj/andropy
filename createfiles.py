import cfgtemplate
import subprocess
import os
import errno
import shlex
from shutil import copyfile
import time
import adbcommands

def writeFile(content, fpath):
	f = open(fpath,"w")
	f.write(content)
	f.close()

def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc:
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else: raise

def create_avd_files(name, avddir, configdir, newavddir, outputpath, avdini, sdsize, isrunning=False):#TODO sd size param
	mkdir_p(outputpath + '/tmp')
	print "Other avd is running: " + str(isrunning)
	avdtemplate = cfgtemplate.template(name, avddir)
	if isrunning == False:
		mkdir_p(newavddir)
		sdcmd = 'mksdcard {} {}'.format(str(sdsize) + 'M', newavddir+ '/sdcard.img')
		subprocess.call(shlex.split(sdcmd))
		adbcommands.check_sd_size(newavddir, sdsize)
		print "SD CREATED"
		avdcreatecommand = 'android create avd -n {0} -t 1'.format(name)
		s1 = subprocess.Popen(avdcreatecommand.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)		
		s1.communicate('no')
		copyfile(configdir + '/' + avdini, newavddir + '/config.ini')
		writeFile(avdtemplate, avddir + '/' +  name + '.ini')
