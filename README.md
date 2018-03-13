# pyWinContext
![](https://i.imgur.com/uqWDQ6y.png)

pyWinContext is a manager for custom context menus, written in Python 3,
supporting Windows 7 and higher. The application allows for complete control
over what filetypes to provide commands to, the text and icons they show with
and the tasks that get performed on the input files.

![Example Configuration](https://i.imgur.com/q9oPy1d.png)
![Working Example](https://i.imgur.com/feGaCrh.png)

## Table of Contents

1. [Installation](#installation)
2. [Command Line Options](#command-line-options)
  1. [Configuration Location](#configuration-location)
3. [Tutorial](#tutorial)
4. [License](#license)

## Installation

For people just wanting to get the application up and running, there are
pre-built releases available at the link below.

[pyWinContext Releases](https://github.com/VodBox/pyWinContext/releases)

If you're installing from source, you will need to have the PyQt5 package (and
cx_Freeze if you wish to build an exe) available on your system. They can
easily be installed using pip.

```batch
pip3 install pyqt5 cx_Freeze
```

From there, you can run the application by launching launch.pyw as admin, or
run the setup script to create an exe (if you have installed cx_Freeze).

```batch
python setup.py build
```

## Command Line Options

### Configuration Location

If you wish to have pyWinContext store it's files in a specificied directory,
instead of a folder in %appdata%, you can do so by passing -c or --config, and
the location of the directory in the command line.

```batch
pyWinContext.exe -c "C:\Users\Example\pyWinContext"
```

## Tutorial

TODO: Basic Tutorial...

## License

This project is licensed under the GPLv3 License - see the [LICENSE](LICENSE) file for details.