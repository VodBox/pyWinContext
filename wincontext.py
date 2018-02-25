#!/usr/bin/python3
# -*- coding: utf-8 -*-

import regutils as reg

import time
import re

import sys
from PyQt5.QtWidgets import QMainWindow, QApplication, QTreeWidgetItem
import app

class ExampleApp(QMainWindow, app.Ui_MainWindow):
	def __init__(self):
		super(self.__class__, self).__init__()
		self.setupUi(self)
		self.initUI()

	def initUI(self):
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
			self.treeWidget_2.topLevelItem(increment).setText(0, type)
			self.treeWidget_2.topLevelItem(increment).setText(1, "")
			fileIncrement = 0
			for file in types[type]:
				item_1 = QTreeWidgetItem(item_0)
				self.treeWidget_2.topLevelItem(increment).child(fileIncrement).setText(0, file["filetype"])
				self.treeWidget_2.topLevelItem(increment).child(fileIncrement).setText(1, file["content-type"])
				fileIncrement += 1
			increment += 1
		self.treeWidget_2.setSortingEnabled(True)
		self.treeWidget_2.sortItems(0, 0)
		self.lineEdit_4.textChanged.connect(self.search_change)
		self.show()

	def search_change(self, text):
		for i in range(0, self.treeWidget_2.topLevelItemCount()):
			for x in range(0, self.treeWidget_2.topLevelItem(i).childCount()):
				if not (text in self.treeWidget_2.topLevelItem(i).child(x).text(0)
					or text in self.treeWidget_2.topLevelItem(i).child(x).text(1)):
					self.treeWidget_2.topLevelItem(i).child(x).setHidden(True)
				else:
					self.treeWidget_2.topLevelItem(i).child(x).setHidden(False)


def main():
	app = QApplication(sys.argv)
	form = ExampleApp()
	form.show()
	app.exec_()


if __name__ == '__main__':
	main()