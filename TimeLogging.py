#/usr/bin/python
# _*_ coding: utf8 _*_

#https://rein.kr/blog/archives/2444

import win32service, win32serviceutil, win32event, servicemanager, win32api
import requests
import wmi, pythoncom
import socket, sys, os
"""url = "http://localhost:5555/logging"
data = "{\"desc\":\"BILL\"}"B
response = requests.post(url,data=data)
print response.json"""

class TimeLogging(win32serviceutil.ServiceFramework):
	_svc_name_ = 'TimeLogging'
	_svc_display_name_ = 'TimeLogging'
	def __init__(self,args):
		win32serviceutil.ServiceFramework.__init__(self,args)
		self.haltEvent = win32event.CreateEvent(None,0,0,None)
		self.url = "http://commuter.tachyon.network/"
		self.UserName = self.GetUserName()
		self.data = {'name': str(self.UserName)}
		self.ReportServiceStatus(win32service.SERVICE_START_PENDING)
		self.timeout = int(1000 * 60 * 60)

	def start(self): pass # To be overridden 
	def stop(self): pass # To be overridden 

	def SvcDoRun(self):
		try:
			servicemanager.LogMsg(servicemanager.EVENTLOG_INFORMATION_TYPE
								, servicemanager.PYS_SERVICE_STARTED
								, (self._svc_name_,""))
			self.ReportServiceStatus(win32service.SERVICE_RUNNING)
			while True:
				try:
					if str(200) in str(self.Arrived()):
						break
				except requests.ConnectionError as ex:
					continue
				except Exception, ex:
					raise ex
				
			self.Main()
			
		except Exception, ex:
			exc_type, exc_obj, exc_tb = sys.exc_info()
			fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
			msg = "\n[+]"+ str(exc_type) +" - "+str(fname) +": "+ str(exc_tb.tb_lineno) + "\t" + str(exc_tb.tb_lineno) +"\n" + str(ex)
			servicemanager.LogInfoMsg(str(msg))
			print msg
			self.SvcStop()
	
	def SvcStop(self):
		self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
		self.Left()
		servicemanager.LogMsg(servicemanager.EVENTLOG_INFORMATION_TYPE
								, servicemanager.PYS_SERVICE_STOPPED
								, (self._svc_name_,""))
		self.ReportServiceStatus(win32service.SERVICE_STOPPED)
		win32event.SetEvent(self.haltEvent)

	def SvcOtherEx(self, control, event_type, data):
		if win32service.SERVICE_CONTROL_PRESHUTDOWN: # To detect "Shutting Down" Message
			servicemanager.LogMsg(servicemanager.EVENTLOG_INFORMATION_TYPE
				, 0xF000 #Generic Message
				, (self._svc_name_,str(self.Left()))) #Generate Heartbeat

	def GetAcceptedControls(self):
		rc = win32serviceutil.ServiceFramework.GetAcceptedControls(self)
		rc |= win32service.SERVICE_ACCEPT_SESSIONCHANGE
		rc |= win32service.SERVICE_ACCEPT_SHUTDOWN
		rc |= win32service.SERVICE_ACCEPT_PRESHUTDOWN
		return rc

	def GetUserName(self):
		pythoncom.CoInitialize()
		WMIinstance = wmi.WMI()
		for item in WMIinstance.Win32_ComputerSystem():
			return item.UserName.split("\\")[-1].upper()

	def Arrived(self):
		while 1:
			response = requests.post(self.url,data=self.data)
			if response.status_code == 200:
				break;		
		return response.json
	def Left(self):
		while 1:
			response = requests.put(self.url,data=self.data)
			if response.status_code == 200:
				break;	
		return response.json

	def Main(self):
		try:
			while 1:
				rc = win32event.WaitForSingleObject(
					self.haltEvent,
					self.timeout)
				if rc == win32event.WAIT_OBJECT_0: #Stop Event
					break
				elif rc == win32event.WAIT_OBJECT_0+1: #OtherEvent
					self.SvcOtherEx()
				elif rc==win32event.WAIT_TIMEOUT:
					self.ReportServiceStatus(win32service.SERVICE_RUNNING) #Maybe, It can be Heartbeat
					servicemanager.LogInfoMsg(str("[+]TimeLogging: HeartBeat"))
				else:
					pass
		except Exception as e:
			exc_type, exc_obj, exc_tb = sys.exc_info()
			fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
			msg = "\n[+]"+ exc_type +" - "+fname +": "+ exc_tb.tb_lineno + "\t" + exc_obj.message
			servicemanager.LogInfoMsg(str(msg))
			print msg

def instart(cls,name,display_name=None,stay_alive=True):
	from os.path import splitext, abspath
	from sys import modules

	cls.__svc_name_ = name
	cls.__svc_display_name_ = display_name
	try:
		module_path=modules[cls.__module__].__file__
	except AttributeError:
		from sys import executable
		module_path=executable
	module_file = splitext(abspath(module_path))
	cls.__svc_reg_class = "%s.%s" % (module_file,cls.__name__)
	if stay_alive: win32api.SetConsoleCtrlHandler(lambda x: True,True)
	try:
		try:
			print "[+] TestModule Started : %s" % (name)
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
			try:
				win32serviceutil.StartService(cls._svc_name_)
			except Exception, e:
				print "[!] %s : %s" %(e.__class__,str(e))
			else:
				print "[+] :::Service started:::"
	except Exception, e:
		print str(e)

if __name__=='__main__':
	win32serviceutil.HandleCommandLine(TimeLogging)	