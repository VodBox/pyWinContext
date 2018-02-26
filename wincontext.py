#! /usr/bin/python3

import regutils as reg

import time
import re

import ctypes
myappid = 'VodBox.pyWinContext.1.0' # arbitrary string
ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

import os
import argparse

parser = argparse.ArgumentParser(description='Manager for Context Menu commands in Windows')
parser.add_argument('-c', '--config', dest='config', default='%appdata%\\pyWinContext', help='Directory for Config and Local Storage')

configLoc = parser.parse_args().config
print(configLoc)


import sys
from PyQt5 import QtCore, QtGui
from PyQt5.QtWidgets import QMainWindow, QApplication, QTreeWidgetItem
import app

class ExampleApp(QMainWindow, app.Ui_MainWindow):
	def __init__(self):
		super(self.__class__, self).__init__()
		self.setupUi(self)
		self.initUI()

	def initUI(self):
		app_icon = QtGui.QIcon()
		app_icon.addFile('images/icon_16.png', QtCore.QSize(16,16))
		app_icon.addFile('images/icon_24.png', QtCore.QSize(24,24))
		app_icon.addFile('images/icon_32.png', QtCore.QSize(32,32))
		app_icon.addFile('images/icon_48.png', QtCore.QSize(48,48))
		app_icon.addFile('images/icon.png', QtCore.QSize(256,256))
		self.setWindowIcon(app_icon)
		self.statusBar().showMessage('Ready')
		self.setWindowTitle('pyWinContext')
		fts = reg.get_file_types()
		types = {}
		types["Other"] = []
		for type in fts:
			p = re.compile('(.+?)\/.+')
			if "perceived-type" in fts[type] and not fts[type]["perceived-type"].capitalize() in types:
				types[fts[type]["perceived-type"].capitalize()] = []
				types[fts[type]["perceived-type"].capitalize()].append({"filetype": type,
					"content-type": fts[type]["content-type"] if "content-type" in fts[type] else ""})
			elif "perceived-type" in fts[type]:
				types[fts[type]["perceived-type"].capitalize()].append({"filetype": type,
					"content-type": fts[type]["content-type"] if "content-type" in fts[type] else ""})
			elif "content-type" in fts[type] and fts[type]["content-type"].capitalize() in types:
				types[fts[type]["content-type"].capitalize()].append({"filetype": type,
					"content-type": fts[type]["content-type"] if "content-type" in fts[type] else ""})
			elif "content-type" in fts[type] and p.match(fts[type]["content-type"]) and p.match(fts[type]["content-type"]).group(1).capitalize() in types:
				types[p.match(fts[type]["content-type"]).group(1).capitalize()].append({"filetype": type,
					"content-type": fts[type]["content-type"] if "content-type" in fts[type] else ""})
			elif "content-type" in fts[type] and p.match(fts[type]["content-type"]):
				types[p.match(fts[type]["content-type"]).group(1).capitalize()] = []
				types[p.match(fts[type]["content-type"]).group(1).capitalize()].append({"filetype": type,
					"content-type": fts[type]["content-type"] if "content-type" in fts[type] else ""})
			else:
				types["Other"].append({"filetype": type,
					"content-type": fts[type]["content-type"] if "content-type" in fts[type] else ""})
		increment = 0
		for type in types:
			item_0 = QTreeWidgetItem(self.treeWidget_2)
			item_0.setCheckState(0, QtCore.Qt.Unchecked)
			item_0.numEnabled = 0
			self.treeWidget_2.topLevelItem(increment).setText(0, type)
			self.treeWidget_2.topLevelItem(increment).setText(1, "")
			fileIncrement = 0
			for file in types[type]:
				item_1 = QTreeWidgetItem(item_0)
				item_1.setCheckState(0, QtCore.Qt.Unchecked)
				self.treeWidget_2.topLevelItem(increment).child(fileIncrement).setText(0, file["filetype"])
				self.treeWidget_2.topLevelItem(increment).child(fileIncrement).setText(1, file["content-type"])
				fileIncrement += 1
			increment += 1
		self.treeWidget.setSortingEnabled(False)
		self.treeWidget_2.setSortingEnabled(True)
		self.treeWidget_2.sortItems(0, 0)
		self.treeWidget.sortItems(0, 0)
		self.treeWidget_2.itemChanged.connect(self.files_change)
		self.treeWidget_2.resizeColumnToContents(0)
		self.lineEdit_4.textChanged.connect(self.search_change)
		self.pushButton_2.clicked.connect(self.group_button)
		self.pushButton_3.clicked.connect(self.command_button)
		self.show()

	def search_change(self, text):
		for i in range(0, self.treeWidget_2.topLevelItemCount()):
			for x in range(0, self.treeWidget_2.topLevelItem(i).childCount()):
				if not (text in self.treeWidget_2.topLevelItem(i).child(x).text(0)
					or text in self.treeWidget_2.topLevelItem(i).child(x).text(1)):
					self.treeWidget_2.topLevelItem(i).child(x).setHidden(True)
				else:
					self.treeWidget_2.topLevelItem(i).child(x).setHidden(False)

	def files_change(self, data):
		parent = data.parent()
		if data.childCount() > 0 and data.checkState(0) != QtCore.Qt.PartiallyChecked:
			checkState = data.checkState(0)
			for childIdx in range(0, data.childCount()):
				oldState = data.treeWidget().blockSignals(True)
				data.child(childIdx).setCheckState(0, checkState)
				data.treeWidget().blockSignals(oldState)
		elif parent != None and type(parent) is QTreeWidgetItem:
			oldState = data.treeWidget().blockSignals(True)

			numEnabled = 0
			for childIdx in range(0, parent.childCount()):
				if data.isSelected() and parent.child(childIdx) != data and parent.child(childIdx).isSelected():
					parent.child(childIdx).setCheckState(0, data.checkState(0))
				numEnabled += (1 if parent.child(childIdx).checkState(0) == QtCore.Qt.Checked else 0)
			if numEnabled == parent.childCount():
				parent.setCheckState(0, QtCore.Qt.Checked)
			elif numEnabled > 0:
				parent.setCheckState(0, QtCore.Qt.PartiallyChecked)
			else:
				parent.setCheckState(0, QtCore.Qt.Unchecked)

			data.treeWidget().blockSignals(oldState)
			
	def add_group(self, name, desc):
		itemGroup = QTreeWidgetItem(self.treeWidget)
		itemGroup.setBackground(0, QtGui.QColor(176, 234, 253))
		itemGroup.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsDragEnabled | QtCore.Qt.ItemIsDropEnabled)
		itemGroup.isCommand = False
		self.treeWidget.topLevelItem(self.treeWidget.topLevelItemCount() - 1).setText(0, name)
		self.treeWidget.topLevelItem(self.treeWidget.topLevelItemCount() - 1).setText(1, desc)
		self.treeWidget.editItem(itemGroup, 0)
	
	def add_command(self, name, desc):
		itemCommand = QTreeWidgetItem(self.treeWidget)
		itemCommand.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsDragEnabled)
		itemCommand.isCommand = True
		self.treeWidget.topLevelItem(self.treeWidget.topLevelItemCount() - 1).setText(0, name)
		self.treeWidget.topLevelItem(self.treeWidget.topLevelItemCount() - 1).setText(1, desc)
		self.treeWidget.editItem(itemCommand, 0)
	
	def group_button(self):
		self.add_group(self.lineEdit_6.displayText() if self.lineEdit_6.displayText() != "" else "Group", "Group Description")
		
	def command_button(self):
		self.add_command("Command", "Command Description")


def main():
	app = QApplication(sys.argv)
	form = ExampleApp()
	form.show()
	app.exec_()


if __name__ == '__main__':
	main()