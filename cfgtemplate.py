def template(avdname, AVDDIR):

	selfname = avdname + '.avd'

	avdtemplate = "avd.ini.encoding=UTF-8\npath={}\npath.rel=avd/{}\ntarget=android-23".format(AVDDIR + '/' + selfname, selfname)

	return avdtemplate