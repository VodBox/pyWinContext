#! /usr/bin/python3

import sys
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import (
    QMainWindow, QMessageBox, QApplication, QTreeWidget,
    QTreeWidgetItem, QFileDialog, QDialog, QListWidgetItem
)
from UI import app,  command

import os
import argparse

import regutils as reg

# import time
import re

import uuid

from pathlib import Path
from collections import OrderedDict
import json

import output


import ctypes
myappid = 'VodBox.pyWinContext.1.0'  # arbitrary string
ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

parser = argparse.ArgumentParser(
    description='Manager for Context Menu commands in Windows')
parser.add_argument(
    '-c', '--config', dest='config', default='%appdata%\\pyWinContext',
    help='Directory for Config and Local Storage')

configLoc = os.path.expandvars(parser.parse_args().config)
configPath = Path(configLoc)
if not configPath.is_dir():
    os.mkdir(configLoc)

print(configLoc)


class ComModes:
    BAT, List = range(2)


if not hasattr(sys, "_MEIPASS"):
    sys._MEIPASS = "."


class WinContextApp(QMainWindow, app.Ui_MainWindow):
    def __init__(self, direct):
        super(self.__class__, self).__init__()
        self.direct = direct
        self.hasChanges = False
        self.setupUi(self)
        self.treeWidget.setSortingEnabled(False)
        self.load()
        self.initUI()

    def closeEvent(self, event):
        if self.hasChanges:
            resBtn = QMessageBox.question(
                self, "pyWinContect", "Save changes before exiting?",
                QMessageBox.Save | QMessageBox.Discard
                | QMessageBox.Cancel, QMessageBox.Save)
            if resBtn == QMessageBox.Cancel:
                event.ignore()
            elif resBtn == QMessageBox.Save:
                save = self.action_save()
                if save:
                    event.accept()
                else:
                    event.ignore()
            return
        event.accept()

    def changes(self):
        self.hasChanges = True
        self.setWindowTitle('* pyWinContext')

    def initUI(self):
        app_icon = QtGui.QIcon()
        app_icon.addFile(
            sys._MEIPASS + '/' + 'images/icon_16.png', QtCore.QSize(16, 16))
        app_icon.addFile(
            sys._MEIPASS + '/' + 'images/icon_24.png', QtCore.QSize(24, 24))
        app_icon.addFile(
            sys._MEIPASS + '/' + 'images/icon_32.png', QtCore.QSize(32, 32))
        app_icon.addFile(
            sys._MEIPASS + '/' + 'images/icon_48.png', QtCore.QSize(48, 48))
        app_icon.addFile(
            sys._MEIPASS + '/' + 'images/icon.png', QtCore.QSize(256, 256))
        self.setWindowIcon(app_icon)
        self.actionExit.triggered.connect(self.close)
        self.actionSave.triggered.connect(self.action_save)
        self.actionSave.setShortcut(QtGui.QKeySequence("Ctrl+S"))
        self.actionImport.triggered.connect(self.action_import)
        self.actionExport.triggered.connect(self.action_export)
        self.setWindowTitle('pyWinContext')
        fts = reg.get_file_types()
        types = {}
        types["Other"] = []
        for type in fts:
            p = re.compile('(.+?)/.+')
            if (
                "perceived-type" in fts[type]
                and not fts[type]["perceived-type"].capitalize() in types
            ):
                types[fts[type]["perceived-type"].capitalize()] = []
                types[fts[type]["perceived-type"].capitalize()].append({
                    "filetype": type,
                    "content-type":
                        fts[type]["content-type"]
                        if "content-type" in fts[type] else ""
                })
            elif "perceived-type" in fts[type]:
                types[fts[type]["perceived-type"].capitalize()].append({
                    "filetype": type,
                    "content-type":
                        fts[type]["content-type"]
                        if "content-type" in fts[type] else ""
                })
            elif (
                "content-type" in fts[type]
                and fts[type]["content-type"].capitalize() in types
            ):
                types[fts[type]["content-type"].capitalize()].append({
                    "filetype": type,
                    "content-type":
                        fts[type]["content-type"]
                        if "content-type" in fts[type] else ""
                })
            elif (
                "content-type" in fts[type]
                and p.match(fts[type]["content-type"])
                and p.match(fts[type]["content-type"]).group(1).capitalize()
                in types
            ):
                cap = p.match(fts[type]["content-type"]).group(1).capitalize()
                types[cap].append({
                    "filetype": type,
                    "content-type":
                        fts[type]["content-type"]
                        if "content-type" in fts[type] else ""
                })
            elif (
                "content-type" in fts[type]
                and p.match(fts[type]["content-type"])
            ):
                cap = p.match(fts[type]["content-type"]).group(1).capitalize()
                types[cap] = []
                types[cap].append({
                    "filetype": type,
                    "content-type":
                        fts[type]["content-type"]
                        if "content-type" in fts[type] else ""
                })
            else:
                types["Other"].append({
                    "filetype": type,
                    "content-type":
                        fts[type]["content-type"]
                        if "content-type" in fts[type] else ""
                })
        for type in types:
            item_0 = QTreeWidgetItem(self.treeWidget_2)
            item_0.setCheckState(0, QtCore.Qt.Unchecked)
            item_0.numEnabled = 0
            item_0.setText(0, type)
            item_0.setText(1, "")
            for file in types[type]:
                item_1 = QTreeWidgetItem(item_0)
                item_1.setCheckState(0, QtCore.Qt.Unchecked)
                item_1.setText(0, file["filetype"])
                item_1.setText(1, file["content-type"])
        self.treeWidget_2.setSortingEnabled(True)
        self.treeWidget_2.sortItems(0, 0)
        self.treeWidget_2.itemChanged.connect(self.files_change)
        self.treeWidget.itemChanged.connect(self.left_bar_change)
        self.lineEdit.textChanged.connect(self.name_change)
        self.lineEdit_2.textChanged.connect(self.desc_change)
        self.treeWidget_2.resizeColumnToContents(0)
        self.treeWidget_2.setDisabled(True)
        self.treeWidget.setSelectionMode(
            QtWidgets.QAbstractItemView.ExtendedSelection)
        self.lineEdit_4.textChanged.connect(self.search_change)
        self.pushButton_2.clicked.connect(self.group_button)
        self.pushButton_3.clicked.connect(self.action_button)
        self.pushButton_4.clicked.connect(self.icon_button)
        self.pushButton_5.clicked.connect(self.clear_button)
        self.pushButton_6.clicked.connect(self.open_command)
        self.pushButton_7.clicked.connect(self.remove_selection)
        self.treeWidget.itemSelectionChanged.connect(self.action_select)
        self.comboBox.currentIndexChanged.connect(self.after_change)
        self.pushButton.clicked.connect(self.add_custom_filetype)
        self.show()
        self.statusBar().showMessage('Ready')

    def load(self):
        config = Path(configLoc + "\\config.json")
        if config.is_file():
            file = open(configLoc + "\\config.json", 'r')
            data = json.loads(file.read(), object_pairs_hook=OrderedDict)
            self.create_items(data, self.treeWidget)
            file.close()

    def create_items(self, data, parent):
        for item in data:
            item = data[item]
            if "command" in item:
                com = self.add_command(
                    item["name"], item["description"], True, parent)
                com.commandMode = item["commandMode"]
                if com.commandMode == ComModes.BAT:
                    com.path = item["command"]
                else:
                    com.commands = item["command"]
                com.filetypes = item["filetypes"]
                com.after = item["after"]
                com.id = item["id"]
                if "icon_path" in item:
                    com.icon_path = item["icon_path"]
                    com.setIcon(0, QtGui.QIcon(item["icon_path"]))
            else:
                group = self.add_group(
                    item["name"], item["description"], True, parent)
                if "icon_path" in item:
                    group.icon_path = item["icon_path"]
                    group.setIcon(0, QtGui.QIcon(item["icon_path"]))
                self.create_items(item["children"], group)

    def action_save(self):
        data = self.get_save_data()
        oldData = None
        config = Path(configLoc + "\\config.json")
        configBak = Path(configLoc + "\\config.json.bak")
        if config.is_file():
            oldFile = open(configLoc + "\\config.json", 'r')
            oldData = json.loads(oldFile.read(), object_pairs_hook=OrderedDict)
            oldFile.close()
            config.replace(configBak)
        file = open(configLoc + "\\config.json", 'w')
        file.write(json.dumps(data, indent=4))
        file.close()
        output.configLoc = configLoc
        output.ComModes = ComModes
        if self.direct:
            output.direct_save(data, oldData)
        else:
            output.reg_save(data, oldData)
        self.hasChanges = False
        self.setWindowTitle('pyWinContext')
        return True

    def action_import(self):
        pass

    def action_export(self):
        pass

    def search_change(self, text):
        for i in range(0, self.treeWidget_2.topLevelItemCount()):
            for x in range(0, self.treeWidget_2.topLevelItem(i).childCount()):
                if not (
                    text
                    in self.treeWidget_2.topLevelItem(i).child(x).text(0)
                    or text
                    in self.treeWidget_2.topLevelItem(i).child(x).text(1)
                ):
                    self.treeWidget_2.topLevelItem(i).child(x).setHidden(True)
                else:
                    self.treeWidget_2.topLevelItem(i).child(x).setHidden(False)

    def add_to_selected(self, filetype):
        self.changes()
        for item in self.treeWidget.selectedItems():
            if item.isCommand and filetype not in item.filetypes:
                item.filetypes.append(filetype)

    def remove_from_selected(self, filetype):
        self.changes()
        for item in self.treeWidget.selectedItems():
            if item.isCommand:
                try:
                    item.filetypes.remove(filetype)
                except ValueError:
                    pass

    def files_change(self, data):
        self.changes()
        parent = data.parent()
        if (
            data.childCount() > 0
            and data.checkState(0) != QtCore.Qt.PartiallyChecked
        ):
            checkState = data.checkState(0)
            for childIdx in range(0, data.childCount()):
                oldState = data.treeWidget().blockSignals(True)
                data.child(childIdx).setCheckState(0, checkState)
                for item in self.treeWidget.selectedItems():
                    if checkState == QtCore.Qt.Checked:
                        self.add_to_selected(data.child(childIdx).text(0))
                    elif checkState == QtCore.Qt.Unchecked:
                        self.remove_from_selected(data.child(childIdx).text(0))
                data.treeWidget().blockSignals(oldState)
        elif parent is not None and type(parent) is QTreeWidgetItem:
            oldState = data.treeWidget().blockSignals(True)
            numEnabled = 0
            for childIdx in range(0, parent.childCount()):
                if (
                    data.isSelected() and parent.child(childIdx) != data
                    and parent.child(childIdx).isSelected()
                ):
                    parent.child(childIdx).setCheckState(0, data.checkState(0))
                if parent.child(childIdx).checkState(0) == QtCore.Qt.Checked:
                    numEnabled += 1
                    self.add_to_selected(parent.child(childIdx).text(0))
                elif (
                    parent.child(childIdx).checkState(0)
                    == QtCore.Qt.PartiallyChecked
                ):
                    numEnabled += 0.1
                elif (
                    parent.child(childIdx).checkState(0)
                    == QtCore.Qt.Unchecked
                ):
                    self.remove_from_selected(parent.child(childIdx).text(0))
            if numEnabled == parent.childCount():
                parent.setCheckState(0, QtCore.Qt.Checked)
            elif numEnabled > 0:
                parent.setCheckState(0, QtCore.Qt.PartiallyChecked)
            else:
                parent.setCheckState(0, QtCore.Qt.Unchecked)
            data.treeWidget().blockSignals(oldState)

    def left_bar_change(self, data):
        self.changes()
        items = self.treeWidget.selectedItems()
        selected = len(items)
        if selected == 1:
            oldState = self.formLayout.blockSignals(True)
            self.lineEdit.setText(items[0].text(0))
            self.lineEdit_2.setText(items[0].text(1))
            self.formLayout.blockSignals(oldState)

    def name_change(self, text):
        self.changes()
        items = self.treeWidget.selectedItems()
        oldState = self.treeWidget.blockSignals(True)
        items[0].setText(0, text)
        self.treeWidget.blockSignals(oldState)

    def desc_change(self, text):
        self.changes()
        items = self.treeWidget.selectedItems()
        oldState = self.treeWidget.blockSignals(True)
        items[0].setText(1, text)
        self.treeWidget.blockSignals(oldState)

    def add_group(self, name, desc, old=False, parent=None):
        if parent is None:
            parent = self.treeWidget
        self.changes()
        itemGroup = QTreeWidgetItem(parent)
        itemGroup.setBackground(0, QtGui.QColor(176, 234, 253))
        itemGroup.setFlags(
            QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEditable
            | QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsEnabled
            | QtCore.Qt.ItemIsDragEnabled | QtCore.Qt.ItemIsDropEnabled)
        itemGroup.isCommand = False
        itemGroup.icon_path = None
        itemGroup.setText(0, name)
        itemGroup.setText(1, desc)
        if not old:
            self.treeWidget.editItem(itemGroup, 0)
        return itemGroup

    def add_command(self, name, desc, old=False, parent=None):
        if parent is None:
            parent = self.treeWidget
        self.changes()
        itemCommand = QTreeWidgetItem(parent)
        itemCommand.setFlags(
            QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEditable
            | QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsEnabled
            | QtCore.Qt.ItemIsDragEnabled)
        itemCommand.isCommand = True
        itemCommand.filetypes = []
        itemCommand.commands = []
        itemCommand.path = ""
        itemCommand.commandMode = ComModes.BAT
        itemCommand.before = None
        itemCommand.after = None
        itemCommand.id = uuid.uuid4().int
        itemCommand.icon_path = None
        itemCommand.setText(0, name)
        itemCommand.setText(1, desc)
        if not old:
            self.treeWidget.setCurrentItem(itemCommand)
            self.treeWidget.editItem(itemCommand, 0)
        return itemCommand

    def group_button(self):
        self.add_group("Group", "Group Description")

    def action_button(self):
        self.add_command("Action", "Action Description")

    def icon_button(self):
        self.changes()
        file = QFileDialog()
        file.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        file.setFileMode(QFileDialog.ExistingFile)
        img = file.getOpenFileUrl(
            filter="Image File (*.png *.jpg *.gif *.bmp)")[0].toLocalFile()
        self.treeWidget.selectedItems()[0].setIcon(0, QtGui.QIcon(img))
        self.treeWidget.selectedItems()[0].icon_path = img
        self.pushButton_5.setEnabled(True)

    def clear_button(self):
        self.changes()
        self.treeWidget.selectedItems()[0].setIcon(0, QtGui.QIcon())
        self.treeWidget.selectedItems()[0].icon_path = None
        self.pushButton_5.setEnabled(False)

    def remove_selection(self):
        self.changes()
        items = self.treeWidget.selectedItems()
        for item in items:
            (
                item.parent()
                or self.treeWidget.invisibleRootItem()
            ).removeChild(item)

    def action_select(self):
        items = self.treeWidget.selectedItems()
        selected = len(items)
        itemCount = 0
        results = {}
        containsCommand = False
        for x in range(0, len(items)):
            if items[x].isCommand:
                containsCommand = True
                itemCount += 1
                for topIdx in range(0, self.treeWidget_2.topLevelItemCount()):
                    top = self.treeWidget_2.topLevelItem(topIdx)
                    for childIdx in range(0, top.childCount()):
                        if top.child(childIdx).text(0) in items[x].filetypes:
                            results[top.child(childIdx).text(0)] = results[
                                top.child(childIdx).text(0)] + 1 if (
                                    top.child(childIdx).text(0) in results
                                ) else 1
                        if x + 1 == len(items):
                            oldState = self.treeWidget_2.blockSignals(True)
                            if (
                                top.child(childIdx).text(0) in results
                                and results[
                                    top.child(childIdx).text(0)
                                ] == itemCount
                            ):
                                top.child(childIdx).setCheckState(
                                    0, QtCore.Qt.Checked)
                            elif top.child(childIdx).text(0) in results:
                                top.child(childIdx).setCheckState(
                                    0, QtCore.Qt.PartiallyChecked)
                            else:
                                top.child(childIdx).setCheckState(
                                    0, QtCore.Qt.Unchecked)
                            self.treeWidget_2.blockSignals(oldState)
        for topIdx in range(0, self.treeWidget_2.topLevelItemCount()):
            self.treeWidget_2.topLevelItem(topIdx).child(0).emitDataChanged()
        if selected == 1 and items[0].isCommand:
            if items[0].icon_path is not None:
                self.pushButton_5.setEnabled(True)
            else:
                self.pushButton_5.setEnabled(False)
            self.treeWidget_2.setDisabled(False)
            oldState = self.formLayout.blockSignals(True)
            self.label.setEnabled(True)
            self.lineEdit.setEnabled(True)
            self.lineEdit.setText(items[0].text(0))
            self.label_2.setEnabled(True)
            self.lineEdit_2.setEnabled(True)
            self.lineEdit_2.setText(items[0].text(1))
            self.label_3.setEnabled(True)
            self.label_6.setEnabled(True)
            self.pushButton_4.setEnabled(True)
            self.pushButton_6.setEnabled(True)
            oldComboState = self.comboBox.blockSignals(True)
            self.comboBox.clear()
            model = QtGui.QStandardItemModel(self.comboBox)
            self.comboBox.setEnabled(True)
            self.label_5.setEnabled(True)
            self.comboBox.setModel(model)
            model.appendRow(QtGui.QStandardItem("None"))
            tree = self.get_full_tree(self.treeWidget, False)
            for item in tree:
                if item is not items[0]:
                    conflict = self.has_conflict(items[0], item)
                    self.comboBox.addItem(
                        self.item_to_string(item), userData=(
                            item if not conflict else None
                        ))
                    model.item(self.comboBox.count()-1, 0).setEnabled(
                        not conflict)
                    if item.id == items[0].after:
                        self.comboBox.setCurrentIndex(self.comboBox.count()-1)
            self.comboBox.blockSignals(oldComboState)
            self.formLayout.blockSignals(oldState)
        else:
            disable = True if selected == 0 or not containsCommand else False
            self.treeWidget_2.setDisabled(disable)
            self.label_3.setEnabled(False)
            if selected == 1:
                self.label.setEnabled(True)
                self.lineEdit.setEnabled(True)
                self.lineEdit.setText(items[0].text(0))
                self.label_2.setEnabled(True)
                self.lineEdit_2.setEnabled(True)
                self.lineEdit_2.setText(items[0].text(1))
                self.label_6.setEnabled(True)
                self.pushButton_4.setEnabled(True)
                if items[0].icon_path is not None:
                    self.pushButton_5.setEnabled(True)
                else:
                    self.pushButton_5.setEnabled(False)
            else:
                self.pushButton_5.setEnabled(False)
                self.label.setEnabled(False)
                self.lineEdit.setEnabled(False)
                self.label_2.setEnabled(False)
                self.lineEdit_2.setEnabled(False)
                self.label_6.setEnabled(False)
                self.pushButton_4.setEnabled(False)
            self.pushButton_6.setEnabled(False)
            self.comboBox.setEnabled(False)
            self.label_5.setEnabled(False)

    def open_command(self):
        self.setEnabled(False)
        item = self.treeWidget.selectedItems()[0]
        dialog = CommandDialog(item)
        dialog.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        if dialog.exec_() == 1:
            self.changes()
        self.setEnabled(True)

    def after_change(self, index):
        self.changes()
        self.treeWidget.selectedItems()[
            0].after = self.comboBox.currentData().id

    def has_conflict(self, item, checkItem):
        idTree = self.create_id_tree(self.treeWidget)
        if checkItem.after is not None and checkItem.after not in idTree:
            checkItem.after = None
        afterItem = (
            idTree[checkItem.after]
            if checkItem.after is not None
            else None
        )
        while afterItem is not None and afterItem != item:
            if afterItem.after is not None and afterItem.after not in idTree:
                afterItem.after = None
            afterItem = (
                idTree[afterItem.after]
                if afterItem.after is not None
                else None
            )
        if afterItem is not None:
            return True
        return False

    def create_id_tree(self, sec):
        res = {}
        count = 0
        if type(sec) is QTreeWidget:
            count = sec.topLevelItemCount()
        else:
            count = sec.childCount()
        for x in range(0, count):
            item = None
            if type(sec) is QTreeWidget:
                item = sec.topLevelItem(x)
            else:
                item = sec.child(x)
            if item.isCommand:
                res[item.id] = item
            else:
                nest = self.create_id_tree(item)
                res.update(nest)
        return res

    def get_full_tree(self, tree, mode):
        result = []
        for topIdx in range(0, tree.topLevelItemCount()):
            top = tree.topLevelItem(topIdx)
            if top.isCommand:
                result.append(top)
            else:
                if mode:
                    result.append({'parent': top})
                    result[len(result)-1]["child"] = self.get_sub_tree(
                        top, mode)
                else:
                    result += self.get_sub_tree(top, mode)
        return result

    def get_sub_tree(self, item, mode):
        result = []
        for childIdx in range(0, item.childCount()):
            sub = item.child(childIdx)
            if sub.isCommand:
                result.append(sub)
            else:
                if mode:
                    result.append({'parent': sub})
                    result[len(result)-1]["child"] = self.get_sub_tree(
                        sub, mode)
                else:
                    result += self.get_sub_tree(sub, mode)
        return result

    def get_save_data(self):
        tree = self.get_full_tree(self.treeWidget, True)
        return self.tree_to_json(tree)

    def tree_to_json(self, tree):
        res = OrderedDict({})
        for item in tree:
            if type(item) is QTreeWidgetItem:
                name = item.text(0) + "-"
                if type(tree) is QTreeWidgetItem:
                    name += str(tree.indexOfChild(item))
                elif type(tree) is QTreeWidget:
                    name += str(tree.indexOfTopLevelItem(item))
                else:
                    name += str(tree.index(item))
                res[name] = {}
                res[name]["commandMode"] = item.commandMode
                res[name]["command"] = (
                    item.commands
                    if item.commandMode != ComModes.BAT
                    else item.path
                )
                res[name]["after"] = item.after
                res[name]["name"] = item.text(0)
                res[name]["filetypes"] = item.filetypes
                res[name]["description"] = item.text(1)
                res[name]["id"] = item.id
                res[name]["icon_path"] = item.icon_path
            else:
                name = item["parent"].text(0) + "-"
                if type(tree) is QTreeWidgetItem:
                    name += str(tree.indexOfChild(item["parent"]))
                elif type(tree) is QTreeWidget:
                    name += str(tree.indexOfTopLevelItem(item["parent"]))
                else:
                    name += str(tree.index(item))
                res[name] = {}
                res[name]["children"] = self.tree_to_json(item["child"])
                res[name]["name"] = item["parent"].text(0)
                res[name]["description"] = item["parent"].text(1)
                res[name]["icon_path"] = item["parent"].icon_path
        return res

    def item_to_string(self, item):
        text = item.text(0)
        parent = item.parent()
        while parent is not None:
            text = parent.text(0) + "\\" + text
            parent = parent.parent()
        return text

    def add_custom_filetype(self):
        self.changes()
        if not hasattr(self, "custom"):
            custom = QTreeWidgetItem(self.treeWidget_2)
            custom.setText(0, "Custom")
            custom.setCheckState(0, QtCore.Qt.Unchecked)
            self.treeWidget_2.addTopLevelItem(custom)
            self.custom = custom
        filetype = self.lineEdit_5.text()
        filetype = filetype if filetype.startswith(".") else "." + filetype
        newItem = QTreeWidgetItem(self.custom)
        newItem.setText(0, filetype)
        newItem.setFlags(
            QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEditable
            | QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsEnabled)
        newItem.setCheckState(0, QtCore.Qt.Unchecked)
        self.custom.addChild(newItem)


class CommandDialog(QDialog, command.Ui_Command):
    def __init__(self, widget):
        super(self.__class__, self).__init__()
        self.setupUi(self)
        self.action = widget
        self.initUI()

    def save(self):
        if self.action.commandMode == ComModes.BAT:
            self.action.path = self.path
        else:
            self.action.commands = []
            for x in range(self.listWidget.count()):
                self.action.commands.append(self.listWidget.item(x).text())

    def initUI(self):
        app_icon = QtGui.QIcon()
        app_icon.addFile(
            sys._MEIPASS + '/' + 'images/icon_16.png', QtCore.QSize(16, 16))
        app_icon.addFile(
            sys._MEIPASS + '/' + 'images/icon_24.png', QtCore.QSize(24, 24))
        app_icon.addFile(
            sys._MEIPASS + '/' + 'images/icon_32.png', QtCore.QSize(32, 32))
        app_icon.addFile(
            sys._MEIPASS + '/' + 'images/icon_48.png', QtCore.QSize(48, 48))
        app_icon.addFile(
            sys._MEIPASS + '/' + 'images/icon.png', QtCore.QSize(256, 256))
        self.setWindowIcon(app_icon)
        self.radioButton.toggled.connect(self.radio_change)
        self.accepted.connect(self.save)
        self.radio_change(self.action.commandMode == ComModes.BAT)
        self.command_select()
        self.path = (
            self.action.path
            if hasattr(self.action, "path")
            else None
        )
        for com in self.action.commands:
            self.add_command(True).setText(com)
        self.pushButton.clicked.connect(self.get_file)
        self.pushButton_2.clicked.connect(self.add_command)
        self.pushButton_3.clicked.connect(self.remove_command)
        self.pushButton_4.clicked.connect(self.move_up)
        self.pushButton_5.clicked.connect(self.move_down)
        self.listWidget.itemSelectionChanged.connect(self.command_select)

    def radio_change(self, state):
        oldState = self.blockSignals(True)
        self.listWidget.setEnabled(not state)
        self.pushButton_2.setEnabled(not state)
        self.pushButton_3.setEnabled(not state)
        self.pushButton_4.setEnabled(not state)
        self.pushButton_5.setEnabled(not state)
        self.pushButton.setEnabled(state)
        self.label.setEnabled(state)
        self.action.commandMode = (ComModes.BAT if state else ComModes.List)
        self.radioButton.setChecked(state)
        self.radioButton_2.setChecked(not state)
        self.blockSignals(oldState)

    def resizeEvent(self, event):
        if self.path is not None:
            fMetrics = QtGui.QFontMetricsF(QtGui.QFont())
            self.label.setText(fMetrics.elidedText(
                self.path, QtCore.Qt.ElideRight, self.label.width() - 15
            ))

    def get_file(self):
        file = QFileDialog()
        file.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        file.setFileMode(QFileDialog.ExistingFile)
        self.path = file.getOpenFileUrl(
            filter="Windows Batch File (*.bat)")[0].toLocalFile()
        fMetrics = QtGui.QFontMetricsF(QtGui.QFont())
        self.label.setText(fMetrics.elidedText(
            self.path, QtCore.Qt.ElideRight, self.label.width() - 15
        ))

    def add_command(self, old=False):
        itemCommand = QListWidgetItem(self.listWidget)
        itemCommand.setFlags(
            QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEditable
            | QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsDragEnabled
        )
        itemCommand.command = ""
        itemCommand.setText("<empty>")
        if not old:
            self.listWidget.setCurrentItem(itemCommand)
            self.listWidget.editItem(itemCommand)
        return itemCommand

    def remove_command(self):
        for item in self.listWidget.selectedItems():
            self.listWidget.takeItem(self.listWidget.row(item))

    def move_up(self):
        count = self.listWidget.count()
        items = [None] * count
        for item in self.listWidget.selectedItems():
            items[self.listWidget.row(item)] = item
        prev = None
        for x in range(0, len(items)):
            item = items[x]
            if item is None:
                if prev is not None:
                    self.listWidget.insertItem(x - 1, prev)
                    prev = None
                prev = self.listWidget.takeItem(x)
        if prev is not None:
            self.listWidget.insertItem(count - 1, prev)

    def move_down(self):
        count = self.listWidget.count()
        items = [None] * count
        for item in self.listWidget.selectedItems():
            items[self.listWidget.row(item)] = item
        prev = None
        for x in range(len(items) - 1, -1, -1):
            item = items[x]
            if item is None:
                if prev is not None:
                    self.listWidget.insertItem(x + 1, prev)
                    prev = None
                prev = self.listWidget.takeItem(x)
        if prev is not None:
            self.listWidget.insertItem(0, prev)

    def command_select(self):
        option = False
        if len(self.listWidget.selectedItems()) > 0:
            option = True
        self.pushButton_3.setEnabled(option)
        self.pushButton_4.setEnabled(option)
        self.pushButton_5.setEnabled(option)


def main(direct):
    app = QApplication(sys.argv)
    ui = WinContextApp(direct)
    ui.show()
    app.exec_()


if __name__ == '__main__':
    main(False)
