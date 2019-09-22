file desciption:


code:
pycontrol.ui - Qt Template (created in Qt Designer)
core.pyw - launch file
func.py - list of functions used in scripts




compile:
0 translate.ui - convert qt-template to python code
0 make 64bits - create executable 64 bits file for Windows
0 make 32bits - create executable 32 bits file for Windows
install.bat - auto install modules depents on this project

addit:
pyuic5.exe - convertor from qt template to python code


installation Windows:

1. install Python 3.x
2. install Qt Designer (for modify pycontrol.ui)
3. run install.bat
4. Take pyuic5.exe from Python 3.x/Scripts installed directory
5. translate XML GUI code to python code with '0 translate.ui.py'
6. run core.pyw or run '0 make 64bits.py' for create executable 64bit version

compiling win64 version (if you have only 32 bits just use 32bits scripts):

0. install python 3.x amd64 and run install.bat
1. set up make 64 py script and run it.
2. run make clean 64.bat
3. copy settings.py

compiling win32 version (if additional):

0. install python 3.x win32 and run manually pip.exe from installed dir and install selected in .bat modules
1. set up make 32 py script and run it.
2. run make clean 32.bat
3. copy settings.py




