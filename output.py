import regutils
import json
import os
import sys
import subprocess
import uac_wrapper
from collections import OrderedDict
from pathlib import Path
from time import sleep
from PIL import Image

configLoc = os.path.expandvars("%appdata%\\pyWinContext")
ComModes = None

def reg_save(data, oldData):
	global completed
	completed = {}
	comStorePath = Path(configLoc + "\\comStore")
	if not comStorePath.is_dir():
		os.mkdir(configLoc + "\\comStore")
	runPath = Path(configLoc + "\\run")
	if not runPath.is_dir():
		os.mkdir(configLoc + "\\run")
	iconPath = Path(configLoc + "\\iconStore")
	if not iconPath.is_dir():
		os.mkdir(configLoc + "\\iconStore")
	outData = data_to_out(data)
	#print(json.dumps(outData))#, indent=2))
	if oldData != None:
		result = "Windows Registry Editor Version 5.00\r\n\r\n"
		result += create_reg_clear(oldData)
		result += create_reg_add(data)
		file = open(configLoc + "\\run\\Setup.reg", "w")
		file.write(result)
		file.close()
		result = "Windows Registry Editor Version 5.00\r\n\r\n"
		result += create_reg_clear(data)
		file = open(configLoc + "\\run\\Remove.reg", "w")
		file.write(result)
		file.close()
	else:
		result = "Windows Registry Editor Version 5.00\r\n\r\n"
		result += create_reg_add(data)
		file = open(configLoc + "\\run\\Setup.reg", "w")
		file.write(result)
		file.close()
		result = "Windows Registry Editor Version 5.00\r\n\r\n"
		result += create_reg_clear(data)
		file = open(configLoc + "\\run\\Remove.reg", "w")
		file.write(result)
		file.close()
	subprocess.Popen(["explorer", "/select," + configLoc + "\\run\\Setup.reg"])

def direct_save(data, oldData):
	outData = data_to_out(data)
	if oldData != None:
		direct_clear(oldData)
	
def create_reg_clear(data):
	result = ""
	outData = data_to_out(data)
	for filetype in outData["filetypes"]:
		info = outData["filetypes"][filetype]
		for command in info["commands"]:
			result += "[-HKEY_CLASSES_ROOT\\SystemFileAssociations\\" + filetype + "\\shell\\pyWin-" + command["regname"] + "]\r\n\r\n"
		for group in info["groups"]:
			result += "[-HKEY_CLASSES_ROOT\\SystemFileAssociations\\" + filetype + "\\shell\\pyWin-" + group + "]\r\n\r\n"
	for command in outData["commandStore"]:
		result += "[-HKEY_LOCAL_MACHINE\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Explorer\\CommandStore\\shell\\pyWin-" + outData["commandStore"][command]["regname"] + "]\r\n\r\n"
	return result
	
def create_reg_add(data):
	result = ""
	outData = data_to_out(data)
	for filetype in outData["filetypes"]:
		result += "[HKEY_CLASSES_ROOT\\SystemFileAssociations\\" + filetype + "\\shell]\r\n\r\n"
		info = outData["filetypes"][filetype]
		for command in info["commands"]:
			result += "[HKEY_CLASSES_ROOT\\SystemFileAssociations\\" + filetype + "\\shell\\pyWin-" + command["regname"] + "]\r\n"
			result += "@=\"" + command["description"].replace('"', '\\"') + "\"\r\n\r\n"
			result += "[HKEY_CLASSES_ROOT\\SystemFileAssociations\\" + filetype + "\\shell\\pyWin-" + command["regname"] + "\\command]\r\n"
			result += "@=\"cmd /c " + configLoc.replace("\\", "\\\\") + "\\\\comStore\\\\" + str(command["id"]) + ".bat %1\"\r\n"
			if "icon_path" in command and command["icon_path"] != None:
				create_icon(command["icon_path"], command["id"])
				result += "\"Icon\"=\"" + configLoc.replace("\\", "\\\\") + "\\\\iconStore\\\\" + str(command["id"]) + ".ico,0\"\r\n"
			result += "\r\n"
			create_bat(command)
		for group in info["groups"]:
			groupObj = info["groups"][group]
			result += "[HKEY_CLASSES_ROOT\\SystemFileAssociations\\" + filetype + "\\shell\\pyWin-" + group + "]\r\n"
			result += "\"MUIVerb\"=\"" + groupObj["name"] + "\"\r\n"
			coms = ""
			newSub = ""
			for com in groupObj["coms"]:
				if coms != "":
					coms += ";"
				if type(com) is int:
					coms += "pyWin-" + outData["commandStore"][com]["regname"]
				else:
					for key in com:
						coms += "pyWin-" + filetype + "-" + key
						newSub += create_sub_commands(filetype, com[key], key, outData)
			result += "\"SubCommands\"=\"" + coms + "\"\r\n"
			if "icon_path" in groupObj and groupObj["icon_path"] != None:
				create_icon(groupObj["icon_path"], group)
				result += "\"Icon\"=\"" + configLoc.replace("\\", "\\\\") + "\\\\iconStore\\\\" + group + ".ico,0\"\r\n"
			result += "\r\n"
			result += newSub
	for command in outData["commandStore"]:
		com = outData["commandStore"][command]
		result += "[HKEY_LOCAL_MACHINE\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Explorer\\CommandStore\\shell\\pyWin-" + com["regname"] + "]\r\n"
		result += "@=\"" + com["description"] + "\"\r\n"
		if "icon_path" in com and com["icon_path"] != None:
				create_icon(com["icon_path"], com["id"])
				result += "\"Icon\"=\"" + configLoc.replace("\\", "\\\\") + "\\\\iconStore\\\\" + str(com["id"]) + ".ico,0\"\r\n"
		result += "\r\n"
		result += "[HKEY_LOCAL_MACHINE\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Explorer\\CommandStore\\shell\\pyWin-" + com["regname"] + "\\command]\r\n"
		result += "@=\"cmd /c " + configLoc.replace("\\", "\\\\") + "\\\\comStore\\\\" + str(com["id"]) + ".bat \\\"%1\\\"\"\r\n\r\n"
		create_bat(com)
	return result
	
def data_to_out(data):
	res = create_db()
	for key in data:
		item = data[key]
		if "command" in item:
			create_bat(item)
			for ft in item["filetypes"]:
				if ft not in res['filetypes']:
					create_filetype(res, ft)
				res['filetypes'][ft]['commands'].append(item)
				res['filetypes'][ft]['commands'][-1]['regname'] = key
		else:
			data_out_nest(res, item, key)
	return res
			
def data_out_nest(res, data, parent):
	for key in data["children"]:
		item = data["children"][key]
		if "command" in item:
			for ft in item["filetypes"]:
				if ft not in res['filetypes']:
					create_filetype(res, ft)
				if parent not in res['filetypes'][ft]['groups']:
					create_group(res, ft, parent, data["description"], data["icon_path"])
				res["commandStore"][item['id']] = item
				res["commandStore"][item['id']]['regname'] = parent + '-' + key
				res['filetypes'][ft]['groups'][parent]['coms'].append(item['id'])
		else:
			temp = create_db()
			data_out_nest(temp, item, key)
			for comKey in temp["commandStore"]:
				res["commandStore"][comKey] = temp["commandStore"][comKey]
				res["commandStore"][comKey]['regname'] = parent + '-' + res["commandStore"][comKey]['regname']
			for ft in temp["filetypes"]:
				if ft not in res["filetypes"]:
					create_filetype(res, ft)
				if parent not in res['filetypes'][ft]['groups']:
					create_group(res, ft, parent, data["description"], data["icon_path"])
				for group in temp['filetypes'][ft]['groups']:
					res['filetypes'][ft]['groups'][parent]['coms'].append(dict([(group, temp['filetypes'][ft]['groups'][group])]))
					
def create_db():
	return {
		'commandStore': {},
		'filetypes': {}
	}
					
def create_filetype(res, ft):
	res['filetypes'][ft] = {}
	res['filetypes'][ft]['commands'] = []
	res['filetypes'][ft]['groups'] = {}
	
def create_group(res, ft, parent, name, icon_path):
	res['filetypes'][ft]['groups'][parent] = {'name': name, 'icon_path': icon_path}
	res['filetypes'][ft]['groups'][parent]['coms'] = []
	
completedBat = {}
completedIcon = {}
	
def create_bat(command):
	if command["id"] not in completedBat:
		completedBat[command["id"]] = True
		file = open(configLoc + "\\comStore\\" + str(command["id"]) + ".bat", 'w')
		batString = "@echo off"
		if command["commandMode"] == ComModes.BAT:
			batString += "\r\ncmd /c " + command["command"] + " %1"
		else:
			for com in command["command"]:
				batString += "\r\n" + com
		if command["after"]:
			batString += "\r\ncmd /c " + configLoc + "\\comStore\\" + str(command["after"]) + ".bat %1"
		file.write(batString)
		file.close()
		
def create_icon(icon_path, id):
	if id not in completedIcon:
		img = Image.open(icon_path)
		icon_sizes = [(16,16), (32, 32), (48, 48), (64,64)]
		img.save(configLoc + "\\iconStore\\" + str(id) + ".ico", sizes=icon_sizes)
		
	
def create_sub_commands(filetype, data, key, outData):
	result = "[HKEY_LOCAL_MACHINE\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Explorer\\CommandStore\\shell\\pyWin-" + filetype + "-" + key + "]\r\n"
	result += "\"MUIVerb\"=\"" + data["name"] + "\"\r\n"
	coms = ""
	newSub = ""
	for com in data["coms"]:
		if coms != "":
			coms += ";"
		if type(com) is int:
			coms += "pyWin-" + outData["commandStore"][com]["regname"]
		else:
			for key in com:
				coms += "pyWin-" + filetype + "-" + com[key]["name"]
				newSub += create_sub_commands(filetype, com[key], key, outData)
	result += "\"SubCommands\"=\"" + coms + "\"\r\n\r\n"
	result += newSub
	return result
	

def direct_clear(data):
	pass
	
def main():
	file = open("C:\\Users\\Dillon\\AppData\\Roaming\\pyWinContext\\config.json", 'r')
	data = json.loads(file.read(), object_pairs_hook=OrderedDict)
	file.close()
	reg_save(data, data)
	
if __name__ == '__main__':
	main()