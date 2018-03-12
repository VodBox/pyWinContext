import sys
from cx_Freeze import setup, Executable

# Dependencies are automatically detected, but it might need fine tuning.
build_exe_options = {"excludes": ["PyQt5.QtWebEngine"], "optimize": 2, "include_files": "images/"}

# GUI applications require a different base on Windows (the default is for a
# console application).
base = None
if sys.platform == "win32":
    base = "Win32GUI"

setup(  name = "pyWinContext",
		targetName = "pyWinContext",
        version = "0.1.1",
        description = "Manager for Context Menu commands in Windows",
        options = {"build_exe": build_exe_options},
        executables = [Executable("uac_wrapper.pyw", base=base, targetName="pyWinContext.exe", icon="icon.ico")])