file desciption:


code:
pycontrol.ui - Qt Template (created in Qt Designer)
core.pyw - launch file
func.py - list of functions used in scripts
fs.py - file system functions


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

1. make.py install
2. make.py translate
3. make.py make 64
4. make.py clear 64
or make.py auto
after copy settings.py


compiling win32 version (if additional):

1. make.py install
2. make.py translate
3. make.py make 32
4. make.py clear 32
after copy settings.py




