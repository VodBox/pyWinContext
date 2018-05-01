import regutils as reg
import json
import os
import subprocess
from collections import OrderedDict
from pathlib import Path
from PIL import Image

configLoc = os.path.expandvars("%appdata%\\pyWinContext")
ComModes = None


def reg_save(data, oldData):
    global completedBat, completedIcon
    completedBat = {}
    completedIcon = {}
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
    if oldData is not None:
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
    global completedBat, completedIcon
    completedBat = {}
    completedIcon = {}
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
    if oldData is not None:
        direct_clear(oldData)
    direct_add(data)


def create_reg_clear(data):
    result = ""
    outData = data_to_out(data)
    for filetype in outData["filetypes"]:
        info = outData["filetypes"][filetype]
        for command in info["commands"]:
            result += "[-HKEY_CLASSES_ROOT\\SystemFileAssociations\\"
            result += filetype + "\\shell\\pyWin-" + command["regname"]
            result += "]\r\n\r\n"
        for group in info["groups"]:
            result += "[-HKEY_CLASSES_ROOT\\SystemFileAssociations\\"
            result += filetype + "\\shell\\pyWin-" + group + "]\r\n\r\n"
    for command in outData["commandStore"]:
        result += "[-HKEY_LOCAL_MACHINE\\SOFTWARE\\Microsoft\\Windows"
        result += "\\CurrentVersion\\Explorer\\CommandStore\\shell\\pyWin-"
        result += outData["commandStore"][command]["regname"] + "]\r\n\r\n"
    return result


def direct_clear(data):
    outData = data_to_out(data)
    for filetype in outData["filetypes"]:
        info = outData["filetypes"][filetype]
        for command in info["commands"]:
            reg.remove_file_association(
                filetype, "pyWin-" + command["regname"])
        for group in info["groups"]:
            reg.remove_file_association(filetype, "pyWin-" + group)
    for command in outData["commandStore"]:
        reg.remove_command_store(
            "pyWin-" + outData["commandStore"][command]["regname"])


def create_reg_add(data):
    result = ""
    outData = data_to_out(data)
    for filetype in outData["filetypes"]:
        result += "[HKEY_CLASSES_ROOT\\SystemFileAssociations\\"
        result += filetype + "\\shell]\r\n\r\n"
        info = outData["filetypes"][filetype]
        for command in info["commands"]:
            result += "[HKEY_CLASSES_ROOT\\SystemFileAssociations\\" + filetype
            result += "\\shell\\pyWin-" + command["regname"] + "]\r\n"
            result += "@=\"" + command["description"].replace('"', '\\"')
            result += "\"\r\n\r\n"
            result += "[HKEY_CLASSES_ROOT\\SystemFileAssociations\\"
            result += filetype + "\\shell\\pyWin-" + command["regname"]
            result += "\\command]\r\n"
            result += "@=\"cmd /c " + configLoc.replace("\\", "\\\\")
            result += "\\\\comStore\\\\" + str(command["id"]) + ".bat %1\"\r\n"
            if "icon_path" in command and command["icon_path"] is not None:
                create_icon(command["icon_path"], command["id"])
                result += "\"Icon\"=\"" + configLoc.replace("\\", "\\\\")
                result += "\\\\iconStore\\\\" + str(command["id"])
                result += ".ico,0\"\r\n"
            result += "\r\n"
            create_bat(command)
        for group in info["groups"]:
            groupObj = info["groups"][group]
            result += "[HKEY_CLASSES_ROOT\\SystemFileAssociations\\"
            result += filetype + "\\shell\\pyWin-" + group + "]\r\n"
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
                        newSub += create_sub_commands(
                            filetype, com[key], key, outData)
            result += "\"SubCommands\"=\"" + coms + "\"\r\n"
            if "icon_path" in groupObj and groupObj["icon_path"] is not None:
                create_icon(groupObj["icon_path"], group)
                result += "\"Icon\"=\"" + configLoc.replace("\\", "\\\\")
                result += "\\\\iconStore\\\\" + group + ".ico,0\"\r\n"
            result += "\r\n"
            result += newSub
    for command in outData["commandStore"]:
        com = outData["commandStore"][command]
        result += "[HKEY_LOCAL_MACHINE\\SOFTWARE\\Microsoft\\Windows"
        result += "\\CurrentVersion\\Explorer\\CommandStore\\shell\\pyWin-"
        result += com["regname"] + "]\r\n"
        result += "@=\"" + com["description"] + "\"\r\n"
        if "icon_path" in com and com["icon_path"] is not None:
                create_icon(com["icon_path"], com["id"])
                result += "\"Icon\"=\"" + configLoc.replace("\\", "\\\\")
                result += "\\\\iconStore\\\\" + str(com["id"]) + ".ico,0\"\r\n"
        result += "\r\n"
        result += "[HKEY_LOCAL_MACHINE\\SOFTWARE\\Microsoft\\Windows"
        result += "\\CurrentVersion\\Explorer\\CommandStore\\shell\\pyWin-"
        result += com["regname"] + "\\command]\r\n"
        result += "@=\"cmd /c " + configLoc.replace("\\", "\\\\")
        result += "\\\\comStore\\\\" + str(com["id"])
        result += ".bat \\\"%1\\\"\"\r\n\r\n"
        create_bat(com)
    return result


def direct_add(data):
    outData = data_to_out(data)
    for filetype in outData["filetypes"]:
        info = outData["filetypes"][filetype]
        for command in info["commands"]:
            iconPath = None
            if "icon_path" in command and command["icon_path"] is not None:
                create_icon(command["icon_path"], command["id"])
                iconPath = configLoc + "\\iconStore\\" + str(command["id"])
                iconPath += ".ico,0"
            reg.create_command(
                "pyWin-" + command["regname"], command["description"],
                "cmd /c " + configLoc + "\\comStore\\" + str(command["id"])
                + ".bat %1", filetype, iconPath)
            create_bat(command)
        for group in info["groups"]:
            groupObj = info["groups"][group]
            iconPath = None
            if "icon_path" in groupObj and groupObj["icon_path"] is not None:
                create_icon(groupObj["icon_path"], group)
                iconPath = configLoc + "\\iconStore\\" + group + ".ico,0"
            coms = ""
            for com in groupObj["coms"]:
                if coms != "":
                    coms += ";"
                if type(com) is int:
                    coms += "pyWin-" + outData["commandStore"][com]["regname"]
                else:
                    for key in com:
                        coms += "pyWin-" + filetype + "-" + key
                        direct_sub(filetype, com[key], key, outData)
            reg.create_group(
                "pyWin-" + group, groupObj["name"], filetype, iconPath, coms)
    for command in outData["commandStore"]:
        com = outData["commandStore"][command]
        iconPath = None
        if "icon_path" in com and com["icon_path"] is not None:
            create_icon(com["icon_path"], com["id"])
            iconPath = configLoc + "\\iconStore\\" + str(com["id"]) + ".ico,0"
        reg.create_sub_command(
            "pyWin-" + com["regname"], com["description"],
            "cmd /c " + configLoc + "\\comStore\\" + str(com["id"])
            + ".bat \"%1\"", iconPath)
        create_bat(com)


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
                    create_group(
                        res, ft, parent, data["description"],
                        data["icon_path"] if "icon_path" in data else None)
                res["commandStore"][item['id']] = item
                res["commandStore"][item['id']]['regname'] = parent + '-' + key
                res['filetypes'][ft]['groups'][parent]['coms'].append(
                    item['id'])
        else:
            temp = create_db()
            data_out_nest(temp, item, key)
            for comKey in temp["commandStore"]:
                res["commandStore"][comKey] = temp["commandStore"][comKey]
                res["commandStore"][comKey]['regname'] = parent + '-'
                + res["commandStore"][comKey]['regname']
            for ft in temp["filetypes"]:
                if ft not in res["filetypes"]:
                    create_filetype(res, ft)
                if parent not in res['filetypes'][ft]['groups']:
                    create_group(
                        res, ft, parent, data["description"],
                        data["icon_path"])
                for group in temp['filetypes'][ft]['groups']:
                    res['filetypes'][ft]['groups'][parent]['coms'].append(
                        dict([(group, temp['filetypes'][ft]['groups'][group])])
                        )


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
    res['filetypes'][ft]['groups'][parent] = {
        'name': name, 'icon_path': icon_path
    }
    res['filetypes'][ft]['groups'][parent]['coms'] = []


completedBat = {}
completedIcon = {}


def create_bat(command):
    if command["id"] not in completedBat:
        completedBat[command["id"]] = True
        file = open(
            configLoc + "\\comStore\\" + str(command["id"]) + ".bat", 'w')
        batString = "@echo off"
        if command["commandMode"] == ComModes.BAT:
            batString += "\r\ncmd /c " + command["command"] + " %1"
        else:
            for com in command["command"]:
                batString += "\r\n" + com
        if command["after"]:
            batString += "\r\ncmd /c " + configLoc + "\\comStore\\"
            batString += str(command["after"]) + ".bat %1"
        file.write(batString)
        file.close()


def create_icon(icon_path, id):
    if id not in completedIcon:
        completedIcon[id] = True
        img = Image.open(icon_path)
        icon_sizes = [(16, 16), (32, 32), (48, 48), (64, 64)]
        make_square(img).save(
            configLoc + "\\iconStore\\" + str(id) + ".ico", sizes=icon_sizes)


def make_square(im, min_size=72, fill_color=(0, 0, 0, 0)):
    x, y = im.size
    size = max(min_size, x, y)
    new_im = Image.new('RGBA', (size, size), fill_color)
    new_im.paste(im, ((size - x) // 2, (size - y) // 2))
    return new_im


def create_sub_commands(filetype, data, key, outData):
    result = "[HKEY_LOCAL_MACHINE\\SOFTWARE\\Microsoft\\Windows\\"
    result += "CurrentVersion\\Explorer\\CommandStore\\shell\\pyWin-"
    result += filetype + "-" + key + "]\r\n"
    result += "\"MUIVerb\"=\"" + data["name"] + "\"\r\n"
    coms = ""
    newSub = ""
    for com in data["coms"]:
        if coms != "":
            coms += ";"
        if type(com) is int:
            coms += "pyWin-" + outData["commandStore"][com]["regname"]
        else:
            for subkey in com:
                coms += "pyWin-" + filetype + "-" + com[key]["name"]
                newSub += create_sub_commands(filetype, com[key], key, outData)
    result += "\"SubCommands\"=\"" + coms + "\"\r\n\r\n"
    if (
        "icon_path" in data and data["icon_path"] is not None
        and data["icon_path"] != ""
    ):
        create_icon(data["icon_path"], data["name"])
        result += "\"Icon\"=\"" + configLoc.replace("\\", "\\\\")
        result += "\\\\iconStore\\\\" + data["name"] + ".ico,0\"\r\n"
    result += newSub
    return result


def direct_sub(filetype, data, key, outData):
    coms = ""
    for com in data["coms"]:
        if coms != "":
            coms += ";"
        if type(com) is int:
            coms += "pyWin-" + outData["commandStore"][com]["regname"]
        else:
            for subkey in com:
                coms += "pyWin-" + filetype + "-" + subkey
                direct_sub(filetype, com[subkey], subkey, outData)
    iconPath = None
    if (
        "icon_path" in data and data["icon_path"] is not None
        and data["icon_path"] != ""
    ):
        create_icon(data["icon_path"], data["name"])
        iconPath = configLoc + "\\iconStore\\" + data["name"] + ".ico,0"
    reg.create_sub_group(
        "pyWin-" + filetype + "-" + key, data["name"], iconPath, coms)


def main():
    file = open(
        "C:\\Users\\Dillon\\AppData\\Roaming\\pyWinContext\\config.json", 'r')
    data = json.loads(file.read(), object_pairs_hook=OrderedDict)
    file.close()
    reg_save(data, data)


if __name__ == '__main__':
    main()
