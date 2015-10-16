""" Template for the devices ini-file in the android avd main folder. Gets copied in the createfiles-module """
def template(avdname, avddir):

	selfname = avdname + '.avd'

	avdtemplate = "avd.ini.encoding=UTF-8\npath={}\npath.rel=avd/{}\ntarget=android-23".format(avddir + '/' + selfname, selfname)

	return avdtemplate
