#! /usr/bin/python3

import launch_dialog
import sys, ctypes
from PyQt5 import QtCore, QtGui
from PyQt5.QtWidgets import QDialog, QApplication

myappid = 'VodBox.pyWinContext.1.0' # arbitrary string
ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

class LaunchDialog(QDialog, launch_dialog.Ui_Dialog):
	def __init__(self):
		super(self.__class__, self).__init__()
		self.setupUi(self)
		import wincontext
		self.win = wincontext.WinContextApp(False)
		self.win.hide()
		self.initUI()
		
	def initUI(self):
		app_icon = QtGui.QIcon()
		app_icon.addFile('images/icon_16.png', QtCore.QSize(16,16))
		app_icon.addFile('images/icon_24.png', QtCore.QSize(24,24))
		app_icon.addFile('images/icon_32.png', QtCore.QSize(32,32))
		app_icon.addFile('images/icon_48.png', QtCore.QSize(48,48))
		app_icon.addFile('images/icon.png', QtCore.QSize(256,256))
		self.setWindowIcon(app_icon)
		self.setWindowFlags(QtCore.Qt.Dialog | QtCore.Qt.CustomizeWindowHint | QtCore.Qt.WindowTitleHint);
		self.pushButton.clicked.connect(self.launch)
		
	def launch(self):
		if self.radioButton.isChecked():
			self.hide()
			self.win.show()
		else:
			import uac_wrapper
			uac_wrapper.run()
			self.hide()
			self.win.show()
			self.win.direct = True
		
def main():
	app = QApplication(sys.argv)
	ui = LaunchDialog()
	ui.show()
	app.exec_()


if __name__ == '__main__':
	main()