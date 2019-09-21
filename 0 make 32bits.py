import os
dll_dir = "\"C:\\Program Files (x86)\\Windows Kits\\10\\Redist\\ucrt\\DLLs\\x86\""
os.system('C:\python37-low\Scripts\pyinstaller.exe --paths %s  --onefile --noconsole core.pyw' % dll_dir)

#  --paths C:\Python35\Lib\site-packages\PyQt5\Qt\bin
# --noconsole
# --paths "C:\Program Files (x86)\Windows Kits\10\Redist\ucrt\DLLs\x86"