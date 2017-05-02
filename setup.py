#/usr/bin/python
# _*_ coding: utf8 _*_

from distutils.core import setup
import py2exe, pip

class Target:
	def __init__(self,**kw):
		self.__dict__.update(kw)
		self.version = "0.1.0.170307"
		self.company_name = "network.tachyon"
		self.copyright = "Copyright (C) 2017 Tachyon@tachyon.network"
		self.name = "TimeLoggingService"
		self.__PackageList=("wmi","requests","pypiwin32")

	def __checkDependancy(self,package):
		try:
			__import__(package)
		except: ImportError:
			pip.main(['install',package])

target = Target(
	description = "Logging Time and Name you arrived and left the office",
	modules=["TimeLogging"],
	cmdline_style='pywin32'
)

setup(service = [target])