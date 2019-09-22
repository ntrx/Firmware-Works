cd dist/core

del PyQt5\Qt\bin\d3dcompiler_47.dll
del PyQt5\Qt\bin\libEGL.dll
del PyQt5\Qt\bin\libGLESv2.dll
del PyQt5\Qt\bin\opengl32sw.dll
	
del PyQt5\Qt\plugins\iconengines\qsvgicon.dll
rmdir /S /Q PyQt5\Qt\plugins\imageformats
del PyQt5\Qt\plugins\platforms\qmminimal.dll
del PyQt5\Qt\plugins\platforms\qoffscreen.dll
del PyQt5\Qt\plugins\platforms\qwebgl.dll
del PyQt5\Qt\plugins\platformthemes\qxdgdesktopportal.dll
del PyQt5\Qt\plugins\platforms\styles\qwindowvistastyle.dll
rmdir /S /Q PyQt5\translations

del libGLESv2.dll
del MSVCP140.dll
del Qt5DBus.dll
del Qt5Network.dll
del Qt5Qml.dll
del Qt5Quick.dll
del Qt5Svg.dll
del Qt5WebSockets.dll
del VCRUNTIME140.dll

del _bz2.pyd
del _ctypes.pyd
del _decimal.pyd
del _hashlib.pyd
del _lzma.pyd
del pyexpat.pyd

pause