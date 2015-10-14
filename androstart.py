import subprocess
import os
import sys
from argparser import get_args
import time
import readline

def get_input(process):
	inpt = raw_input("Cancel program?[Yn]\n")
	if inpt == "Y" or input == "Yes" or input == "y":
		process.kill()
	else:
		get_input(process)

selfpath = os.path.dirname(os.path.abspath(__file__))
volfilepath = selfpath + '/voltool/volprog.py'
get_args(sys.argv[1:])

androcmd = 'python {}/andropy.py'.format(selfpath)
argstring = ""
for s in sys.argv[1:]:
	argstring += ' ' + s
s = subprocess.Popen(['xterm', '-e',androcmd + argstring])


get_input(s)
'python', volfilepath
s.communicate()
print "Android dump-process closed"
print "Starting the volatility helping tool"

volcmd = 'python ' + volfilepath
subprocess.Popen(['lxterminal', '-e', volcmd])
