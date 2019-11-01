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
2. install Qt Designer (If you need to edit Qt File)
3. run make.py install (install required modules)
4. Take pyuic5.exe from Python 3.x/Scripts installed directory (if you need p.2)
5. translate XML GUI code to python code with make.py translate (if you need p.2)
6. Make sure that settings.py is available with core.pyw or executable file.
7. run core.pyw or run 'make.py make 64' for create executable 64bit version


compiling win64 version (if you have only 32 bits just use 32bits scripts):

1. make.py install
2. make.py translate
3. make.py make 64
4. make.py clear 64
or make.py auto
now copy settings.py


compiling win32 version (if additional):

1. make.py install
2. make.py translate
3. make.py make 32
4. make.py clear 32
now copy settings.py




