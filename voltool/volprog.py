"""
This script basically only prefixes the issued volatility-command with the profile-prefix. For easier handeling, some methods like -write, -all were implemented, to save the user the work of doing one command for every dump.
Script starts in its current directory, so one needs to change to the directory where the dumps are located with -changedir.

"""
import os
import subprocess
import sys
import re
import argparse
import shlex
import readline


class CmdBuilder:

	def __init__(self, volfile, profile):
		self.cmdprefix = 'python {} --profile={} '.format(volfile, profile)

	def buildcmd(self, fpath, cmd, tofilecmd = False):
		if tofilecmd != False:
			fname = os.path.basename(fpath[1:-1])
			exname = fname.rstrip('.dump')
			exname = exname.strip('lime')
			exname = '"' + tofilecmd + exname + '.txt"'
			cmd = cmd + ' > ' + exname

		return self.cmdprefix + "-f " + fpath + " " + cmd

class Dumpclass:

	def __init__(self, cmdbuilder, dumpfiles):
		self.cmdbuilder = cmdbuilder
		self.dumpfiles = dumpfiles

	def every_dump(self, cmd, tofilecmd = False):
		for f in self.dumpfiles:
			self.single_dump(cmd, f, tofilecmd)


	def single_dump(self, cmd , f, tofilecmd = False):
		print '\033[94m' + 'File: ' + f + '\033[0m'
		command = self.cmdbuilder.buildcmd(f, cmd, tofilecmd)
		subprocess.call(['/bin/bash', '-c', command])


	def single_bash(self, cmd):
		p = subprocess.Popen(['/bin/bash', '-c', cmd],stdout=subprocess.PIPE)
		print p.communicate()[0]


class Vshell:

	dumpfiles = []
	vol_commands = ['linux_pslist',  'linux_psaux',  'linux_pstree',  'linux_pslist_cache',  'linux_pidhashtable',  'linux_psxview',  'linux_lsof',  'linux_memmap',  'linux_proc_maps',  'linux_dump_map',  'linux_bash',  'linux_lsmod',  'linux_moddump',  'linux_tmpfs',  'linux_check_afinfo',  'linux_check_tty',  'linux_keyboard_notifier',  'linux_check_creds',  'linux_check_fop',  'linux_check_idt',  'linux_check_syscall',  'linux_check_modules',  'linux_check_creds',  'linux_arp',  'linux_ifconfig',  'linux_route_cache',  'linux_netstat',  'linux_pkt_queues',  'linux_sk_buff_cache',  'linux_cpuinfo',  'linux_dmesg',  'linux_iomem',  'linux_slabinfo',  'linux_mount',  'linux_mount_cache',  'linux_dentry_cache',  'linux_find_file',  'linux_vma_cache']
	prefixlist = ['-one', '-all', 'exit', '-changedir', '-h', '-hvol']

	def __init__(self, dumppath, volfile, volprofile):
		self.dumppath = dumppath
		self.volfile = volfile
		self.volprofile = volprofile
		#sets self.dumpfiles
		self.get_file_list()
		cmdbuilder = CmdBuilder(self.volfile, self.volprofile)
		self.dumpclass = Dumpclass(cmdbuilder, self.dumpfiles)
		self.build_arg_parser()


	def build_arg_parser(self):
		self.parser = argparse.ArgumentParser(description='Helps for examining or extracting volatility-memory-dumps', add_help=False)
		self.parser.add_argument('-all', '--allfiles', action="store_true", help='operation for all files in directory. Does not work together with -one')
		self.parser.add_argument('-one', '--onefile', action="store_true", help='operation for one file in the directory.Does not work together with -all')
		self.parser.add_argument('-f', '--filename', help='name of the file. Required for a single file from the directory')
		self.parser.add_argument('-w', '--writeoutput', action="store_true", required=False, help='writes the output of the volatility-command to a file')
		self.parser.add_argument('errorflag', help=argparse.SUPPRESS, action="store_false")
		self.parser.add_argument("items",nargs=argparse.REMAINDER)

	def parse_input(self, rawinput):
		args = self.parser.parse_args(rawinput)
		if (args.allfiles and args.onefile):
			print "Error: -allfiles and -onefile selected"
			args.errorflag = True
		if (args.onefile) and (not args.filename):
			print "Error - a filename in the current directory  must be specified for the onefile operation."
			args.errorflag = True
		if len(args.items) == 0:
			print "Error - no command specified"
			args.errorflag = True
		return args

	def printable_list(self, l):
		rstring = l[0]
		seperator = ', '
		for s in l[1:]:
			rstring += seperator + s
		return rstring

	def print_hvol(self):
		print "Volatility commands: " + self.printable_list(self.vol_commands)

	def print_prefix_help(self):
		print "Allowed commands start with: " + self.printable_list(self.prefixlist)

	def exit_self(self):
		print "Thank you for using volhelper"
		exit()

	def run(self):
		while True :
			self.getinput()

	def getinput(self):
		inputcmd = raw_input("\nIssue your command and confirm with [Enter]. For help, type -h or -hvol for an overview of volatility-commands. Current working-directory: {}\n".format(self.dumppath))
		if len(inputcmd.strip()) == 0 or re.match(r'^[_\W]+$', inputcmd):
			print "Error - invalid string composition"
			return
		if inputcmd == 'exit':
			self.exit_self()
		elif inputcmd == '-hvol':
			self.print_hvol()
			return
		elif '-changedir' in inputcmd:
			newdir = inputcmd.strip('-changedir').strip()
			if os.path.isdir(newdir):
				self.change_dumppath(newdir)
				print "working-directory changed to " + newdir
			else:
				print "Error: " + newdir + " is not a valid directory"
			return
		splitcmd = shlex.split(inputcmd)
		prefix = splitcmd[0]

		if prefix not in self.prefixlist:
				print "Looks like a normal bash command, executing. Keep in mind that not every bash-operation is fully  supported. Type -h or -hvol for a list of commands."
				self.dumpclass.single_bash(inputcmd)
		else:
			args = self.parse_input(splitcmd)
			if args.errorflag == True:
				return
			vol_cmd = args.items[0]
			if not vol_cmd in self.vol_commands:
				print "Error - no volatility command specified after args. Canceling command."
				return
			#print args
			fname = False
			s = " ";
			cmdstring =  s.join(args.items)
			#the volatility cmd, f.e. -all -write >linux_memmap< -p 7047
			if args.writeoutput:
				fname = vol_cmd

			if args.allfiles:
				self.dumpclass.every_dump(cmdstring, fname)
			elif args.onefile:
				self.dumpclass.single_dump(cmdstring , args.filename, fname)

	def get_file_list(self):
		for file in os.listdir(self.dumppath):
			if file.endswith(".dump"):
				self.dumpfiles.append('"' + self.dumppath + "/" + file + '"')

	def change_dumppath(self, dumppath):
		self.dumppath = dumppath
		self.get_file_list()
		cmdbuilder = CmdBuilder(self.volfile, self.volprofile)
		self.dumpclass = Dumpclass(cmdbuilder, self.dumpfiles)


#size compare? check if open error in volatility. mark as faulty? TODO

def volread_argparse(*args):
	parser = argparse.ArgumentParser(description='Starts the volatility-helper tool')
	parser.add_argument('-n', '--samplepath', required=False,help='folder of the malware sample-dumps')
	args = parser.parse_args()
	if (args.samplepath) and (not os.path.isdir(args.samplepath)):
		raise Exception("Error : the specified string is not pointing to a directory")
	return args.samplepath



if __name__ == '__main__':
	samplepath = volread_argparse(sys.argv[1:])
	if samplepath is not None:
		dumppath = samplepath
	else:
		dumppath =  os.path.dirname(os.path.abspath(__file__))#current folder
	volfile = "/home/santoku4/volatility/vol.py"
	volprofile = "LinuxGoldfish-3_4ARM"
	sshell = Vshell(dumppath, volfile, volprofile)
	sshell.run()
