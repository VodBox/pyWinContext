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
    1. [Basic Tutorial](#basic-tutorial)
4. [License](#license)

## Installation

For people just wanting to get the application up and running, there are
pre-built releases available at the link below.

[pyWinContext Releases](https://github.com/VodBox/pyWinContext/releases)

If you're installing from source, you will need to have the PyQt5 and Pillow
packages (and PyInstaller if you wish to build an exe) available on your
system. They can easily be installed using pip.

```batch
pip3 install pyqt5 pillow pyinstaller
```

From there, you can run the application by launching launch.pyw as admin, or
run the setup to create an exe (if you have installed PyInstaller).

```batch
pyinstaller --onefile uac_wrapper.spec
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

### Basic Tutorial

When you first open up pyWinContext, you'll be presented with a window that
looks like this.

![](https://i.imgur.com/GtYExdj.png)

First we start in the left pane of the window to setup our actions. By pressing
the "New Action" button, you can add a new item to the list, with the name
selected and editable.

The name acts as a unique identifier for the action. You can also edit the
description by double clicking the description box. The contents of that box
will be used as the text in the context menu.

![](https://i.imgur.com/7VL5NWf.png)

As an example, we're going to make an action that will show details about a
file in a window, such as name, filetype and file size. As such, I've named the
action "filedetails", and gave it the description "List File Details".

![](https://i.imgur.com/ZjS0TdY.png)

Next, we move to the middle pane to select a filetype we'd like this action to
show for. We can search for a specific filetype to make it easier to find. I'm
going to apply our action to the ".txt" filetype, by searching ".txt" and
ticking it's checkbox.

![](https://i.imgur.com/y8Anvxu.png)

(Note: If a filetype you're looking for isn't shown, you can add it using the
textbox at the bottom of this pane)

Then we move on to the right pane. Here we can set the name and description,
just like the left pane, with the addition that we can also assign an icon if
we want.

![](https://i.imgur.com/v5yblVG.png)

By opening up the command editor, we can actually start to define what our
action does when we click on it.

![](https://i.imgur.com/1BbQr6x.png)

Setting the editor to "Command List" allows us to write our basic script inside
the application itself. By adding commands and writing a few lines, we get
something like this.

![](https://i.imgur.com/2o6JEpm.png)

Hitting OK, and then saving (either through the File > Save menu, or with the
Ctrl + S shortcut) will allow us to test our action.

If you launched with File Export Mode, an Explorer window with two registry
files will open. To install our action, we use the Setup.reg file.

![](https://i.imgur.com/NJOhYvz.png)

If you launched with Direct Edit Mode, changes will have been applied in the
background. All we need to do, is find .txt file, right click it, and see if
our action shows up.

![](https://i.imgur.com/6JHpA9u.png)

It worked! And we get to see what our script does when we execute it.

![](https://i.imgur.com/ZRZ1pJH.png)

Anything that can be executed from a batch script will work with pyWinContext,
so the possibilities for using command line applications and automation tools
are endless.

These are just the basics. With groups added into the picture, you can start to
build up nested menus and folders for all your actions, like in the preview
picture at the top of the page, and help immensely with automation.

## Variables

Please find a list of variables usable in the commands [here](https://ss64.com/nt/syntax-args.html)
## License

This project is licensed under the GPLv3 License - see the [LICENSE](LICENSE) file for details.
