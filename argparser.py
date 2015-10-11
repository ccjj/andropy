def get_args():
	import argparse
	import os
	from sys import exit
	
	parser = argparse.ArgumentParser(description='Automates android memory dumping')
	parser.add_argument('-n', '--samplepath', required=True,help='path of the malware sample-apk')
	parser.add_argument('-i', '--interval', required=True, type=int, help='intervals for each memory dump in seconds')
	parser.add_argument('-d', '--sdcard', type=int, required=False, help='dump will be saved on the sdcard of the android device instead of being transfered over TCP')
	parser.add_argument('-o', '--outputpath', required=False, help='path of the output-path')
	parser.add_argument('-c', '--customconfig', required=False, help='path of a custom avd config.ini')

	args = parser.parse_args()
	if not os.path.isfile(args.samplepath) or (args.customconfig is not None and os.path.isfile(args.customconfig)):
		raise Exception("error : one or more specified paths are not pointing to a file")
	return args.samplepath, args.interval, args.sdcard, args.outputpath, args.customconfig
	
	
if __name__ == '__main__':
	import sys
	get_args(sys.argv[1:])
#AVDNAME = os.path.splitext(args.samplepath)[0]
#AVDPATH = args.samplepath
#os.path.isfile(fname) 
#print(AVDNAME)