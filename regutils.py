import winreg
import time

def create_sub_command(name, desc, command, icon):
	hkey = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,'Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\CommandStore\\shell',0,winreg.KEY_ALL_ACCESS|winreg.KEY_WOW64_64KEY)
	key = winreg.CreateKey(hkey, name)
	winreg.SetValueEx(key, "", 0, winreg.REG_SZ, desc)
	winreg.SetValue(key, "command", winreg.REG_SZ, command)
	if icon != None:
		winreg.SetValueEx(key, "Icon", 0, winreg.REG_SZ, icon)
	else:
		winreg.SetValueEx(key, "Icon", 0, winreg.REG_SZ, "")
	winreg.SetValueEx(key, "direct", 0, winreg.REG_SZ, "Yes")

def create_sub_group(name, desc, icon, coms):
	key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,'Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\CommandStore\\shell',0,winreg.KEY_ALL_ACCESS|winreg.KEY_WOW64_64KEY)
	comKey = winreg.CreateKey(key, name)
	winreg.SetValueEx(comKey, "MUIVerb", 0, winreg.REG_SZ, desc)
	winreg.SetValueEx(comKey, "SubCommands", 0, winreg.REG_SZ, coms)
	winreg.SetValueEx(comKey, "Direct", 0, winreg.REG_SZ, "Yes")
	if icon != None:
		winreg.SetValueEx(comKey, "Icon", 0, winreg.REG_SZ, icon)
	else:
		winreg.SetValueEx(comKey, "Icon", 0, winreg.REG_SZ, "")

def create_group(name, desc, filetype, icon, coms):
	key = winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, "SystemFileAssociations\\" + filetype + "\\shell")
	comKey = winreg.CreateKey(key, name)
	winreg.SetValueEx(comKey, "MUIVerb", 0, winreg.REG_SZ, desc)
	winreg.SetValueEx(comKey, "SubCommands", 0, winreg.REG_SZ, coms)
	if icon != None:
		winreg.SetValueEx(comKey, "Icon", 0, winreg.REG_SZ, icon)
	else:
		winreg.SetValueEx(comKey, "Icon", 0, winreg.REG_SZ, "")

def create_command(name, desc, command, filetype, icon):
	key = winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, "SystemFileAssociations\\" + filetype + "\\shell")
	comKey = winreg.CreateKey(key, name)
	winreg.SetValue(key, name, winreg.REG_SZ, desc)
	if icon != None:
		winreg.SetValue(comKey, "Icon", winreg.REG_SZ, icon)
	winreg.CreateKey(comKey, "command")
	winreg.SetValue(comKey, "command", winreg.REG_SZ, command)

def get_file_types():
	keys = {}
	length = winreg.QueryInfoKey(winreg.HKEY_CLASSES_ROOT)[0]
	for i in range(0, length):
		subkey = winreg.EnumKey(winreg.HKEY_CLASSES_ROOT, i)
		if subkey.startswith("."):
			theclass = winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, subkey)
			keys[subkey] = {}
			try:
				keys[subkey]["content-type"] = winreg.QueryValueEx(theclass, "Content Type")[0]
			except Exception as e:
				pass
			try:
				keys[subkey]["perceived-type"] = winreg.QueryValueEx(theclass, "PerceivedType")[0]
			except Exception as e:
				pass
	return keys

def remove_file_association(filetype, name):
	key = winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, "SystemFileAssociations\\" + filetype + "\\shell")
	comKey = winreg.CreateKey(key, name)
	remove_all_sub_keys(comKey)
	winreg.DeleteKey(key, name)

def remove_command_store(name):
	key = winreg.CreateKey(winreg.HKEY_LOCAL_MACHINE, "SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Explorer\\CommandStore\\shell")
	comKey = winreg.CreateKey(key, name)
	remove_all_sub_keys(comKey)
	winreg.DeleteKey(key, name)

def remove_all_sub_keys(key):
	index = 0
	length = winreg.QueryInfoKey(key)[0]
	for i in range(0, length):
		try:
			subname = winreg.EnumKey(key, i)
			subkey = winreg.CreateKey(key, subname)
			remove_all_sub_keys(subkey)
			winreg.DeleteKey(key, subname)
		except OSError as e:
			pass
