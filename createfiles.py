import cfgtemplate
import subprocess
import os
import errno
import shlex
from shutil import copyfile
import time

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
	avdtemplate = cfgtemplate.template(name, avddir)
	if isrunning == False:
		mkdir_p(newavddir)
		command2 = "mksdcard {} {}/sdcard.img".format(str(sdsize) + 'M', newavddir)
		subprocess.call(command2.split())
		time.sleep(1.0)
		command = 'echo no |android create avd -n {0} -t 1'.format(name)
		s1 = subprocess.Popen(['/bin/bash', '-c', command], stdout=subprocess.PIPE)
		s1.wait()
		copyfile(configdir + '/' + avdini, newavddir + '/config.ini')
		writeFile(avdtemplate, avddir + '/' +  name + '.ini')
