"""
Parses the apk pointed by the samplepath with help of the Android
Asset Packaging Tool(appt). Returns a tuple with packagename/activityname in case of success.
If the lines package or activity could not be found in the aapt-output,
False/False is returned. If something went wrong by parsing, an error is thrown
"""
import subprocess

def get_package_infos(samplepath):
	"""example:
	package: name='h.w' versionCode='1' versionName='a'
	launchable-activity: name='a.a'  label='' icon='' """
	cmd = 'aapt dump badging {} | grep "package\|activity"'.format(samplepath)
	try:
		out = subprocess.Popen(['/bin/bash', '-c', cmd], stdout=subprocess.PIPE)
		for line in out.stdout:
			if "package" in line:
				s = line.lstrip("package: name=")[1:]
				t = s.find("' versionCode='")
				s = s[:t]
				package = s
			elif "activity" in line:
				s = line.lstrip("launchable-activity: name=")[1:]
				t = s.find("'  label='")
				s = s[:t]
				activity = s
		print "Package-name: " + package + "\nActivity-name: " + activity
		if activity is None or package is None:
			print "Error parsing apk - please start the apk when the machine is fully bootet"
			return False, False
		return package, activity
	except IndexError, e:
		print "Error parsing apk - please start the apk when the machine is fully bootet." + e
		return False, False
