#! /usr/bin/python3

import ctypes, sys, time

def is_admin():
	try:
		return ctypes.windll.shell32.IsUserAnAdmin()
	except:
		return False

def run():
	if is_admin():
		return True
	else:
		ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, __file__, None, 1)
		sys.exit()
		
def main():
	run()
	import wincontext
	win = wincontext.main(True)
	win.activateWindow()
	
if __name__ == '__main__':
	main()
