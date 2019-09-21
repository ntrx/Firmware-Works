file desciption:


code:
pycontrol.ui - Qt Template (created in Qt Designer)
core.pyw - launch file
func.py - list of functions used in scripts



scripts:
upload.py - script for upload on device
settings.py - configuration
restart.py - script for restart device
compile.py - script for compile binary file
auto upload then restart.py - auto upgrade firmware on device with options


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

