from TimeLogging import TimeLogging
import win32serviceutil,time

class TestService(TimeLogging):
	def __init__(self,args):
		super.__init__(self,args)

	def SvcDoRun(self):
		self.runflag=True
		super.timeout=1000 * 10
		super.SvcDoRun(self)
		while self.runflag:
			self.Sleep(1)
	def SvcStop(self):
		self.runflag=False
		super.SvcStop()
		print "[+] SvcStop has been triggered"

if __name__ == "__main__":
	import admin
	if not admin.isUserAdmin():
		admin.runAsAdmin()
	else:
		from os.path import splitext, abspath
		from sys import modules
		cls = TestService
		try:
			module_path=modules[cls.__module__].__file__
		except AttributeError:
			from sys import executable
			module_path=executable
		module_file = splitext(abspath(module_path))
		cls.__svc_reg_class = "%s.%s" % (module_file,cls.__name__)

		win32api.SetConsoleCtrlHandler(lambda x: True,True)
		try:
			win32serviceutil.QueryServiceStatus(cls.__name__)
		except:
			win32serviceutil.InstallService(
				cls.__svc_reg_class,
				cls.__svc_name_,
				cls.__svc_display_name_,
				startType=win32service.SERVICE_AUTO_START
			)
			print "[+] Service Has been installed"
		else:
			win32serviceutil.HandleCommandLine(cls,argv=["update"])
		finally:
			win32serviceutil.HandleCommandLine(cls,argv=["debug"])
			try:
				while True:
					time.sleep(1)
			except:
				exit()