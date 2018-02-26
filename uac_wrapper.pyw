#! /usr/bin/python3

import ctypes, sys, time

def is_admin():
	try:
		return ctypes.windll.shell32.IsUserAnAdmin()
	except:
		return False

if is_admin():
	import wincontext
	wincontext.main()
else:
	ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, __file__, None, 1)