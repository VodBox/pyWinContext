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
		ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, ' '.join(sys.argv[1:]), None, 1)
		sys.exit()
		
def run_as_admin(file):
	ctypes.windll.shell32.ShellExecuteW(None, "open", file, "", None, 1)
		
def main():
	run()
	import launch
	win = launch.main()
	
if __name__ == '__main__':
	main()
