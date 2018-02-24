import winreg

def create_sub_command(name, desc, command):
	key = winreg.CreateKey(winreg.HKEY_LOCAL_MACHINE, "SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Explorer\\CommandStore\\shell\\" + name)
	winreg.SetValue(key, "", winreg.REG_SZ, desc)
	comKey = winreg.CreateKey(key, "command")
	winreg.SetValue(comKey, "", winreg.REG_SZ, command)

def link_sub_command(name, desc, comName, filetype):
	key = winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, "SystemFileAssociations\\." + filetype + "\\shell")
	comKey = winreg.CreateKey(key, name)
	winreg.SetValueEx(comKey, "MUIVerb", 0, winreg.REG_SZ, desc)
	subs = ("")
	try:
		subs = winreg.QueryValueEx(comKey, "SubCommands")
	except Exception as e:
		subs = ("")
	winreg.SetValueEx(comKey, "SubCommands", 0, winreg.REG_SZ, ((subs[0] + ";") if subs[0] != "" else "") + comName)

def create_command(name, desc, command, filetype):
	key = winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, "SystemFileAssociations\\." + filetype + "\\shell")
	comKey = winreg.CreateKey(key, name)
	winreg.SetValue(key, name, winreg.REG_SZ, desc)
	winreg.CreateKey(comKey, "command")
	winreg.SetValue(comKey, "command", winreg.REG_SZ, command)

def get_sub_command_string(filetype, name):
	key = winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, "SystemFileAssociations\\." + filetype + "\\shell\\" + name)
	try:
		subs = winreg.QueryValueEx(key, "SubCommands")
		return subs[0]
	except Exception as e:
		return ""

def get_sub_commands(filetype, name):
	subs = get_sub_command_string(filetype, name)
	return subs.split(";")

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
