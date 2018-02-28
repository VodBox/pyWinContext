#! /usr/bin/python3

import launch_dialog
import sys
from PyQt5.QtWidgets import QDialog, QApplication

class LaunchDialog(QDialog, launch_dialog.Ui_Dialog):
	def __init__(self):
		super(self.__class__, self).__init__()
		self.setupUi(self)
		import wincontext
		self.win = wincontext.WinContextApp(False)
		self.win.hide()
		self.initUI()
		
	def initUI(self):
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