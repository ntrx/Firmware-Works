import os
import sys
import shutil

## Arguments list:
# --noconsole - hide console
# --onefile    - portable file
# --path *    - choose path

MAIN_FILE = 'core.pyw'
win32_dll = "\"C:\\Program Files (x86)\\Windows Kits\\10\\Redist\\ucrt\\DLLs\\x86\""
pyinst_32 = "C:\python37-low\Scripts\pyinstaller.exe"
QT_XML = 'pycontrol.ui'
PY_XML = 'gui.py'


def make_64(arguments):
    os.system('pyinstaller %s %s' % (arguments, MAIN_FILE))


def make_32(arguments):
    os.system('%s --path %s %s %s' % (pyinst_32, win32_dll, arguments, MAIN_FILE))


def clear_64():
    os.chdir("dist/core")
    shutil.rmtree("cryptography-2.7-py3.7.egg-info")
    os.remove("PyQt5\\Qt\\bin\\d3dcompiler_47.dll")
    os.remove("PyQt5\\Qt\\bin\\libEGL.dll")
    os.remove("PyQt5\\Qt\\bin\\libGLESv2.dll")
    os.remove("PyQt5\\Qt\\bin\\opengl32sw.dll")         
    os.remove("PyQt5\\Qt\\plugins\\iconengines\\qsvgicon.dll")
    shutil.rmtree("PyQt5\\Qt\\plugins\\imageformats")
    os.remove("PyQt5\\Qt\\plugins\\platforms\\qminimal.dll")
    os.remove("PyQt5\\Qt\\plugins\\platforms\\qoffscreen.dll")
    os.remove("PyQt5\\Qt\\plugins\\platforms\\qwebgl.dll")
    os.remove("PyQt5\\Qt\\plugins\\platformthemes\\qxdgdesktopportal.dll")
    os.remove("PyQt5\\Qt\\plugins\\styles\\qwindowsvistastyle.dll")
    shutil.rmtree("PyQt5\\Qt\\translations")
    os.remove("libGLESv2.dll")
    os.remove("MSVCP140.dll")
    os.remove("Qt5DBus.dll")
    os.remove("Qt5Network.dll")
    os.remove("Qt5Qml.dll")
    os.remove("Qt5Quick.dll")
    os.remove("Qt5Svg.dll")
    os.remove("Qt5WebSockets.dll")
    os.remove("VCRUNTIME140.dll")
    os.remove("_bz2.pyd")
    os.remove("_ctypes.pyd")
    os.remove("_decimal.pyd")
    os.remove("_hashlib.pyd")
    os.remove("_lzma.pyd")
    os.remove("pyexpat.pyd")


def clear_32():
    os.chdir("dist/core")
    os.remove("PyQt5\\Qt\\bin\\d3dcompiler_47.dll")
    os.remove("PyQt5\\Qt\\bin\\libEGL.dll")
    os.remove("PyQt5\\Qt\\bin\\libGLESv2.dll")
    os.remove("PyQt5\\Qt\\bin\\opengl32sw.dll")         
    os.remove("PyQt5\\Qt\\plugins\\iconengines\\qsvgicon.dll")
    shutil.rmtree("PyQt5\\Qt\\plugins\\imageformats")
    os.remove("PyQt5\\Qt\\plugins\\platforms\\qminimal.dll")
    os.remove("PyQt5\\Qt\\plugins\\platforms\\qoffscreen.dll")
    os.remove("PyQt5\\Qt\\plugins\\platforms\\qwebgl.dll")
    os.remove("PyQt5\\Qt\\plugins\\platformthemes\\qxdgdesktopportal.dll")
    os.remove("PyQt5\\Qt\\plugins\\styles\\qwindowsvistastyle.dll")
    shutil.rmtree("PyQt5\\Qt\\translations")
    os.remove("libGLESv2.dll")
    os.remove("MSVCP140.dll")
    os.remove("Qt5DBus.dll")
    os.remove("Qt5Network.dll")
    os.remove("Qt5Qml.dll")
    os.remove("Qt5Quick.dll")
    os.remove("Qt5Svg.dll")
    os.remove("Qt5WebSockets.dll")
    os.remove("VCRUNTIME140.dll")
    os.remove("_bz2.pyd")
    os.remove("_ctypes.pyd")
    os.remove("_decimal.pyd")
    os.remove("_hashlib.pyd")
    os.remove("_lzma.pyd")
    os.remove("pyexpat.pyd")


def install_modules():
    os.system("pip install pyqt5")
    os.system("pip install paramiko")
    os.system("pip install pyinstaller")


def translate():
    os.system("pyuic5.exe %s -o %s" % (QT_XML, PY_XML))

    
def main():
    if len(sys.argv) <= 1:
        print("Not enough arguments. Type %s help" % sys.argv[0])
    else:
        if sys.argv[1] == 'help':
            print('Usage: %s [make|clear|install] [32|64]' % sys.argv[0])
            print('  * make - compiling executable windows file')
            print('  * 32 or 64 - 32bit or 64bit version')
            print('  * install - install requied modules')
            print('  * translate - translate Qt XML file to python code')
            print('  * clear - remove harbage files')
            print('  * auto - perform translate UI - make default - clear default')
            print('Arguments for make:')
            print('  * --noconsole - hide console from executable file')
            print('  * --onefile  - create portable version')
        if sys.argv[1] == 'make':
            if sys.argv[2] == '32':
                args = len(sys.argv)
                if args > 3:
                    arg_command = ""
                    for i in range(3, args):
                        arg_command += sys.argv[i] + " "
                    make_32(arg_command)
                else:
                    make_32("--noconsole --onefile")
            if sys.argv[2] == '64':
                args = len(sys.argv)
                if args > 3:
                    arg_command = ""
                    for i in range(3, args):
                        arg_command += sys.argv[i] + " "
                    make_64(arg_command)
                else:
                    make_64("--noconsole --onefile")
        if sys.argv[1] == 'clear':
            if sys.argv[2] == '32':
                clear_32()
            if sys.argv[2] == '64':
                clear_64()
        if sys.argv[1] == 'install':
            install_modules()
        if sys.argv[1] == 'translate':
            translate()
        if sys.argv[1] == 'auto':
            translate()
            make_64("--noconsole --onefile")


if __name__ == '__main__':
    main()
