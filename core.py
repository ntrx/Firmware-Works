# #!/usr/bin/env python

from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtCore import pyqtSlot, QThread, pyqtSignal
from gui import Ui_MainWindow
import func
import paramiko
import os
import subprocess
import fs


PROG_NAME = "Firmware Works"
VERSION = "1.0.4"
RELEASE = "beta"

SETTINGS_EMPTY: str = ""
SETTINGS_FILE: str = "settings.py"


class Cache_file:
    source: str = "source-history.log"
    project: str = "project-history.log"
    device_ip: str = "device-ip-history.log"
    winscp: str = "winscp-history.log"
    putty: str = "putty-history.log"
    psplash: str = "psplash-history.log"
    list = []

    def init(self):
        listing = []
        paths = vars(self)
        for item in paths:
            listing.append(str(paths[item]))
        for i in range(2, 8):
            self.list.append(listing[i])

        for file in self.list:
            if not os.path.exists(file):
                fs.cache_create(self.list)


class Settings:
    class device:               # Embedded device properties
        user: str = ""               # Username to login
        password: str = ""           # Password to login
        ip: str = ""                 # IP address
        file_protocol: str = ""      # Type of file protocol SFTP or SCP
        ftp_mode: str = ""           # 0 - use paramiko and other build-in pythonic modules, 1 - user WinSCP
        system: int = 0              # 0 - using NXP processors, 1 - using Intem Atom processors

    class server:               # Build-server properties
        user: str = ""               # Username to login
        password: str = ""           # Password to login
        ip: str = ""                 # Server IP
        path_external: str = ""      # PATH to upload sources
        sync_files: str = ""     # sync or upload sources
        compiler: str = ""           # Type of compiler gcc or gcc8
        compile_mode: bool = False   # If true then clean object files before compiling (recompiling)
        using: bool = True           # Linux only: compiling on external build-server or (false) using built-in gcc compiler

    class project:              # Project settings
        name: str = ""               # Name of project which has been applied to output binary file
        path_local: str = ""         # Local PATH of sources
        path_psplash: str = ""       # Local PATH of psplash file

    class local:                # Some miscellaneous properties
        path_winscp: str = ""        # WinSCP local PATH
        path_putty: str = ""         # PuTTy local PATH
        winscp_ok: bool = False      # is WinSCP found
        putty_ok: bool = False       # is PuTTy found

    def load(self):
        if not os.path.exists(SETTINGS_FILE):
            print("User settings not found, creating preset file.")
            self.device.user = 'example_user'
            self.device.ip = '192.168.10.1'
            self.device.password = '1111'
            self.project.name = 'example_proj'
            self.project.path_local = 'C:/example_proj'
            self.server.path_external = '/home/root/'
            self.server.ip = '192.168.10.2'
            self.server.user = 'root'
            self.server.password = '1111'
            self.server.sync_files = '0'
            if os.name == 'nt':
                self.device.ftp_mode = '1'
            else:
                self.device.ftp_mode = '0'
            self.local.path_winscp = 'C:/example'
            self.local.path_putty = 'C:/example'
            self.project.path_psplash = 'C:/example'
            self.save(self)

        # If find == 0 its our parameter (because all they is starting from 0)
        with open(SETTINGS_FILE) as fp:
            for line in fp:
                if line.find('user') == 0:
                    index = 4
                    self.device.user = get_value(line, index)

                if line.find('host') == 0:
                    index = 4
                    self.device.ip = get_value(line, index)

                if line.find('secret') == 0:
                    index = 6
                    self.device.password = get_value(line, index)

                if line.find('project') == 0:
                    index = 7
                    self.project.name = get_value(line, index)

                if line.find('source') == 0:
                    index = 6
                    self.project.path_local = get_value(line, index)

                if line.find('global_build_server') == 0:
                    index = 19
                    self.server.ip = get_value(line, index)

                if line.find('global_bs_user') == 0:
                    index = 14
                    self.server.user = get_value(line, index)

                if line.find('global_bs_secret') == 0:
                    index = 16
                    self.server.password = get_value(line, index)

                if line.find('global_bs_dir') == 0:
                    index = 13
                    self.server.path_external = get_value(line, index)

                if line.find('update') == 0:
                    index = 6
                    self.server.sync_files = get_value(line, index)

                if line.find('ftp_mode') == 0:
                    index = 8

                    if os.name == 'nt':
                        self.device.ftp_mode = get_value(line, index)
                    else:
                        ftp_mode = get_value(line, index)
                        if ftp_mode == '1':
                            self.device.ftp_mode = '0'

                if line.find('path_scp') == 0:
                    index = 8
                    self.local.path_winscp = get_value(line, index)

                if line.find('path_putty') == 0:
                    index = 10
                    self.local.path_putty = get_value(line, index)

                if line.find('path_psplash') == 0:
                    index = 12
                    self.project.path_psplash = get_value(line, index)
            fp.close()

    def save(self):
        fp = open(SETTINGS_FILE, 'w')
        fp.write("# Auto created settings file. Remember that value is framed by '' \n")
        check = check_value(self.device.user)
        fp.write("user = '%s' # user login to device (default: root) \n" % check)
        check = check_value(self.device.ip)
        fp.write("host = '%s' # device IP \n" % check)
        check = check_value(self.device.password)
        fp.write("secret = '%s' # user pass to device (default: empty) \n" % check)
        check = check_value(self.project.name)
        fp.write("project = '%s' # project name (sn4215, sn3307) \n" % check)
        check = check_value(self.project.path_local)
        fp.write("source = '%s' # path to project (must contain: Build, Src) \n" % check)
        check = check_value(self.server.ip)
        fp.write("global_build_server = '%s' # Build-Server IP  \n" % check)
        check = check_value(self.server.user)
        fp.write("global_bs_user = '%s' # Your login to build-server \n" % check)
        check = check_value(self.server.password)
        fp.write("global_bs_secret = '%s' # Pass\n" % check)
        check = check_value(self.server.path_external)
        fp.write("global_bs_dir = '%s' # uploading directory on build-server\n" % check)
        check = check_value(self.server.sync_files)
        fp.write("update = '%s' #  0 - update, 1 - sync \n" % check)
        check = check_value(self.device.ftp_mode)
        fp.write("ftp_mode = '%s' # - 1 - use winSCP, 0 - paramiko  \n" % check)
        check = check_value(self.local.path_winscp)
        fp.write("path_scp = '%s' # - path to WinSCP .com file \n" % check)
        check = check_value(self.local.path_putty)
        fp.write("path_putty = '%s' # - path to Putty exe file \n" % check)
        check = check_value(self.project.path_psplash)
        fp.write("path_psplash = '%s' # - path to pslpash file\n" % check)
        fp.close()

    def init(self, gui):
        fs.cache_read(gui.comboBox_3, MyCache.source)
        fs.cache_read(gui.comboBox, MyCache.project)
        fs.cache_read(gui.comboBox_2, MyCache.device_ip)
        fs.cache_read(gui.comboBox_5, MyCache.putty)
        fs.cache_read(gui.comboBox_4, MyCache.winscp)
        fs.cache_read(gui.comboBox_6, MyCache.psplash)

        cache_files_size = 0

        for file in Cache_file.list:
            cache_files_size += os.path.getsize(file)
        gui.label_13.setText("%s b" % cache_files_size)

        if len(self.project.name) == 0:
            gui.lineEdit.setText(SETTINGS_EMPTY)
        else:
            gui.lineEdit.setText(self.project.name)

        if len(self.device.ip) == 0:
            gui.lineEdit_2.setText(SETTINGS_EMPTY)
        else:
            gui.lineEdit_2.setText(self.device.ip)

        if len(self.device.user) == 0:
            gui.lineEdit_3.setText(SETTINGS_EMPTY)
        else:
            gui.lineEdit_3.setText(self.device.user)

        if len(self.device.password) == 0:
            gui.lineEdit_4.setText(SETTINGS_EMPTY)
        else:
            gui.lineEdit_4.setText(self.device.password)

        if len(self.project.path_local) == 0:
            gui.lineEdit_5.setText(SETTINGS_EMPTY)
        else:
            gui.lineEdit_5.setText(self.project.path_local)

        if len(self.server.ip) == 0:
            gui.lineEdit_6.setText(SETTINGS_EMPTY)
        else:
            gui.lineEdit_6.setText(self.server.ip)

        if len(self.server.user) == 0:
            gui.lineEdit_7.setText(SETTINGS_EMPTY)
        else:
            gui.lineEdit_7.setText(self.server.user)

        if len(self.server.password) == 0:
            gui.lineEdit_8.setText(SETTINGS_EMPTY)
        else:
            gui.lineEdit_8.setText(self.server.password)

        if len(self.server.path_external) == 0:
            gui.lineEdit_12.setText(SETTINGS_EMPTY)
        else:
            gui.lineEdit_12.setText(self.server.path_external)

        if self.device.ftp_mode == '1':
            gui.checkBox_3.setChecked(True)
            gui.radioButton.setEnabled(True)
            gui.radioButton_2.setEnabled(True)
        elif self.device.ftp_mode == '0':
            gui.checkBox_3.setChecked(False)
            gui.radioButton.setEnabled(False)
            gui.radioButton_2.setEnabled(False)
            self.server.sync_files = '0'

        if self.server.sync_files == '0':
            gui.radioButton.setChecked(True)
        elif self.server.sync_files == '1':
            gui.radioButton_2.setChecked(True)

        if len(self.local.path_winscp) == 0:
            gui.lineEdit_9.setText(SETTINGS_EMPTY)
        else:
            if not os.path.isfile(self.local.path_winscp):
                gui.lineEdit_9.setStyleSheet("background-color: red")
                gui.label_9.setText("Some errors found during initialization settings.")
                self.local.winscp_ok = False
            else:
                self.local.winscp_ok = True
            gui.lineEdit_9.setText(self.local.path_winscp)

        if len(self.local.path_putty) == 0:
            gui.lineEdit_10.setText(SETTINGS_EMPTY)
        else:
            if not os.path.isfile(self.local.path_putty):
                gui.lineEdit_10.setStyleSheet("background-color: red")
                gui.label_9.setText("Some errors found during initialization settings.")
                self.local.putty_ok = False
            else:
                self.local.putty_ok = True
            gui.lineEdit_10.setText(self.local.path_putty)

        if len(self.project.path_psplash) == 0:
            gui.lineEdit_11.setText(SETTINGS_EMPTY)
        else:
            gui.lineEdit_11.setText(self.project.path_psplash)

        firmware_path = self.project.path_local + "\\Build\\bin\\" + self.project.name + ".bin"
        fs.path_get_firmware(firmware_path, gui.label_16)


class MySFTPClient(paramiko.SFTPClient):
    def put_dir(self, source, target):
        for item in os.listdir(source):
            if os.path.isfile(os.path.join(source, item)):
                if item.find('.ipch') >= 0:
                    continue
                print("Proceed: %s\\%s [%d]" % (source, item, os.path.getsize(os.path.join(source, item))))
                self.put(os.path.join(source, item), '%s/%s' % (target, item), )
            else:
                self.mkdir('%s/%s' % (target, item), ignore_existing=True)
                self.put_dir(os.path.join(source, item), '%s/%s' % (target, item))

    def mkdir(self, path, mode=511, ignore_existing=False):
        try:
            super(MySFTPClient, self).mkdir(path, mode)
        except IOError:
            if ignore_existing:
                pass
            else:
                raise


class EProgBar(QThread):
    working_status = pyqtSignal(int)

    def run(self):
        self.working_status.emit(1)
        if os.path.exists(Settings.project.path_local):
            func.scp_compile(MySettings, 'release')
        else:
            print('Project PATH not found.')
        self.working_status.emit(0)


class EProgBar_debug(QThread):
    working_status_debug = pyqtSignal(int)

    def run(self):
        self.working_status_debug.emit(1)
        if os.path.exists(Settings.project.path_local):
            func.scp_compile(MySettings, 'debug')
        else:
            print('Project PATH not found.')
        self.working_status_debug.emit(0)


class MainWindow(QtWidgets. QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        # gui init
        super(MainWindow, self).__init__(parent)
        QtWidgets.QMainWindow.__init__(self)
        self.calc = EProgBar()
        self.setupUi(self)
        self.setWindowTitle("%s %s %s" % (PROG_NAME, VERSION, RELEASE))

        if os.name == 'nt': # for windows
            # Compiler type field
            self.label_18.setVisible(False)
            self.comboBox_9.setVisible(False)
            pass
        else: # for linux
            # Tab: External
            self.tabWidget.setTabEnabled(2, False)
            # Compiler type field
            self.label_18.setVisible(True)
            self.comboBox_9.setVisible(True)
            # Button: open with winSCP
            self.pushButton_25.setVisible(False)
            # Button: open with Putty
            self.pushButton_26.setText("open with xterm")
            # Button: putty
            self.pushButton_17.setText("xterm")
            # Button: winSCP
            self.pushButton_24.setVisible(False)

        # self.label_9.setStyleSheet('background-color: red') for future
        MySettings.load(MySettings)
        MyCache.init(MyCache)
        # init text labels and 'end' panel
        MySettings.init(MySettings, self)
        # radioButtons
        self.radioButton_2.clicked.connect(self.on_radioButton_sync_mode)
        self.radioButton.clicked.connect(self.on_radioButton_upload_mode)

        # buttons
        self.pushButton_7.clicked.connect(self.on_button_ping)
        self.pushButton_5.clicked.connect(self.on_button_stop)
        self.pushButton_2.clicked.connect(self.on_button_restart)
        self.pushButton_3.clicked.connect(self.on_button_compile)
        self.pushButton_4.clicked.connect(self.on_button_upload)
        self.pushButton.clicked.connect(self.on_button_auto)
        self.pushButton_6.clicked.connect(self.on_button_save)
        self.pushButton_9.clicked.connect(self.on_button_reload)
        self.pushButton_8.clicked.connect(self.on_button_apply)
        self.pushButton_10.clicked.connect(self.on_button_open)
        self.pushButton_11.clicked.connect(self.on_button_killall)
        self.pushButton_12.clicked.connect(self.on_button_detect)
        self.pushButton_14.clicked.connect(self.on_button_ts_test)
        self.pushButton_13.clicked.connect(self.on_button_ts_calibrate)
        self.pushButton_17.clicked.connect(self.on_open_putty)
        self.pushButton_18.clicked.connect(self.on_button_compile_debug)
        self.pushButton_19.clicked.connect(self.on_button_edit)
        self.pushButton_20.clicked.connect(self.on_button_clear_cache)
        self.pushButton_21.clicked.connect(self.on_button_outdated)
        self.pushButton_22.clicked.connect(self.on_button_psplash)
        self.pushButton_15.clicked.connect(self.on_button_compile_once)
        self.pushButton_16.clicked.connect(self.on_button_compile_debug_once)
        self.pushButton_23.clicked.connect(self.on_button_clean)
        self.pushButton_24.clicked.connect(self.on_button_winscp)
        self.pushButton_25.clicked.connect(self.on_button_bs_winscp)
        self.pushButton_26.clicked.connect(self.on_button_bs_putty)

        # tool buttons
        self.toolButton_2.clicked.connect(self.on_path_project)
        self.toolButton_3.clicked.connect(self.on_path_winscp)
        self.toolButton_4.clicked.connect(self.on_path_putty)
        self.toolButton_5.clicked.connect(self.on_path_psplash)

        # check boxes
        self.checkBox_3.clicked.connect(self.on_winscp_use)

        # comboboxes
        self.comboBox.currentIndexChanged.connect(self.on_project_change)
        self.comboBox_3.currentIndexChanged.connect(self.on_source_change)
        self.comboBox_2.currentIndexChanged.connect(self.on_device_ip_change)
        self.comboBox_4.currentIndexChanged.connect(self.on_winscp_change)
        self.comboBox_5.currentIndexChanged.connect(self.on_putty_change)
        self.comboBox_6.currentIndexChanged.connect(self.on_psplash_change)
        self.comboBox_9.currentIndexChanged.connect(self.on_bs_using_change)
        self.comboBox_10.currentIndexChanged.connect(self.on_system_change)

        # action menu
        self.actionOpen_2.triggered.connect(self.on_button_open)
        self.actionEdit.triggered.connect(self.on_button_edit)
        self.actionPower_off.triggered.connect(self.on_button_poweroff)
        self.actionReboot.triggered.connect(self.on_button_reboot)
        self.actionReload.triggered.connect(self.on_button_reload)
        self.actionSave.triggered.connect(self.on_button_save)
        self.actionRemove.triggered.connect(self.on_act_remove)

    @pyqtSlot(name='on_button_bs_putty')
    def on_button_bs_putty(self):
        if os.name == "nt":
            if MySettings.local.putty_ok:
                func.putty_path(MySettings.server.ip, MySettings.server.user, MySettings.local.path_putty)
            else:
                self.label_9.setText("Putty not found!")
        else:
            os.system("xterm -hold -e 'ssh %s@%s'" % (MySettings.server.user, MySettings.server.ip))

    @pyqtSlot(name='on_button_bs_winscp')
    def on_button_bs_winscp(self):
        winscp_exe = MySettings.local.path_winscp.replace("com", "exe")
        MySettings.device.file_protocol = protocol_get(self)
        command = ("sftp://%s:%s@%s/" % (MySettings.server.user, MySettings.server.password, MySettings.server.ip))
        func.scp_command(command, winscp_exe)

    @pyqtSlot(name='on_button_winscp')
    def on_button_winscp(self):
        winscp_exe = MySettings.local.path_winscp.replace("com", "exe")
        MySettings.device.file_protocol = protocol_get(self)
        if MySettings.device.file_protocol == 'sftp':
            command = ("sftp://%s:%s@%s/" % (MySettings.device.user, MySettings.device.password, MySettings.device.ip))
        elif MySettings.device.file_protocol == 'scp':
            command = ("scp://%s@%s:%s/" % (MySettings.device.user, MySettings.device.ip, MySettings.device.password))
        else:
            return
        func.scp_command(command, winscp_exe)

    @pyqtSlot(name='on_act_remove')
    def on_act_remove(self):
        dest_path = MySettings.project.path_local + "/Build/bin/" + MySettings.project.name + ".bin"
        if os.path.exists(dest_path):
            os.remove(dest_path)
            self.label_9.setText("Firmware remove command.")
        else:
            self.label_9.setText("Nothing to remove, firmware not found.")

    @pyqtSlot(name='on_button_clean')
    def on_button_clean(self):
        MySettings.device.file_protocol = protocol_get(self)
        func.scp_clean(MySettings)
        if Settings.server.using:
            self.label_9.setText("Cleaned firmware on remote server command.")
        else:
            self.label_9.setText("Firmware clean command.")
                

    @pyqtSlot(name='on_radioButton_sync_mode')
    def on_radioButton_sync_mode(self):
        MySettings.server.sync_files = '1'

    @pyqtSlot(name='on_radioButton_upload_mode')
    def on_radioButton_upload_mode(self):
        MySettings.server.sync_files = '0'

    @pyqtSlot(name='on_button_psplash')
    def on_button_psplash(self):
        if func.is_online(MySettings.device.ip):
            MySettings.device.file_protocol = protocol_get(self)
            func.scp_psplash_upload(MySettings, self.label_9)
        else:
            self.label_9.setText("Host is unreachable")

    @pyqtSlot(name='on_psplash_change')
    def on_psplash_change(self):
        self.lineEdit_11.setText(self.comboBox_6.currentText())

    @pyqtSlot(name='on_button_outdated')
    def on_button_outdated(self):
        if func.is_online(MySettings.device.ip):
            MySettings.device.file_protocol = protocol_get(self)
            func.scp_detect_outdated_firmware(MySettings, self.label_9)
        else:
            self.label_9.setText('Host is unreachable')

    @pyqtSlot(name='on_button_detect')
    def on_button_detect(self):
        if func.is_online(MySettings.device.ip):
            func.scp_detect_project(MySettings, self.label_9)
        else:
            self.label_9.setText('Host is unreachable')

    @pyqtSlot(name='on_button_clear_cache')
    def on_button_clear_cache(self):
        fs.cache_create(MyCache.list)
        self.on_button_apply()
        self.label_9.setText("Cached information has been clear.")

    @pyqtSlot(name='on_button_edit')
    def on_button_edit(self):
        if os.name == "nt":
            CREATE_NO_WINDOW = 0x08000000
            return subprocess.Popen("notepad %s" % SETTINGS_FILE, creationflags=CREATE_NO_WINDOW)
        else:
            os.system("xdg-open %s" % SETTINGS_FILE)

    @pyqtSlot(name='on_winscp_change')
    def on_winscp_change(self):
        self.lineEdit_9.setText(self.comboBox_4.currentText())

    @pyqtSlot(name='on_device_ip_change')
    def on_device_ip_change(self):
        self.lineEdit_2.setText(check_value(self.comboBox_2.currentText()))
        
    @pyqtSlot(name='on_putty_change')
    def on_putty_change(self):
        self.lineEdit_10.setText(self.comboBox_5.currentText())
        
    @pyqtSlot(name='on_source_change')
    def on_source_change(self):
        self.lineEdit_5.setText(self.comboBox_3.currentText())

    @pyqtSlot(name='on_project_change')
    def on_project_change(self):
        self.lineEdit.setText(self.comboBox.currentText())
        
    @pyqtSlot(name='on_bs_using_change')
    def on_bs_using_change(self):
        # Tab: Build-Server
        if self.comboBox_9.currentIndex() == 1:  # Build-in compiler
            Settings.server.using = False              
            self.comboBox_9.setCurrentIndex(1)
        elif self.comboBox_9.currentIndex() == 0: # Build-server compiler
            Settings.server.using = True
            self.comboBox_9.setCurrentIndex(0)
        self.tabWidget.setTabEnabled(1, Settings.server.using)

    @pyqtSlot(name='on_system_change')
    def on_system_change(self):
        if self.comboBox_10.currentIndex() == 0: # NXP iMX6(QP)
            Settings.device.system = 0
            self.comboBox_10.setCurrentIndex(0)
            self.comboBox_7.setEnabled(True)
            # Disabling autorun.sh scripts and project detecting
            self.pushButton_12.setEnabled(True)
            self.pushButton_11.setEnabled(True)
            self.pushButton_2.setEnabled(True)
            self.pushButton_5.setEnabled(True)
            # Disabling sensor functions and upload firmware/psplash
            self.pushButton_14.setEnabled(True)
            self.pushButton_13.setEnabled(True)
            self.pushButton_22.setEnabled(True)
            self.pushButton_4.setEnabled(True)
            self.pushButton.setEnabled(True)
            self.checkBox.setEnabled(True)
            self.checkBox_2.setEnabled(True)
        elif self.comboBox_10.currentIndex() == 1: # Intel Atom
            Settings.device.system = 1
            self.comboBox_10.setCurrentIndex(1)
            # Only gcc there
            self.comboBox_7.setCurrentIndex(0)
            self.comboBox_7.setEnabled(False)
            # Disabling autorun.sh scripts and project detecting
            self.pushButton_12.setEnabled(False)
            self.pushButton_11.setEnabled(False)
            self.pushButton_2.setEnabled(False)
            self.pushButton_5.setEnabled(False)
            # Disabling sensor functions and upload firmware/psplash
            self.pushButton_14.setEnabled(False)
            self.pushButton_13.setEnabled(False)
            self.pushButton_22.setEnabled(False)
            self.pushButton_4.setEnabled(False)
            self.pushButton.setEnabled(False)
            self.checkBox.setEnabled(False)
            self.checkBox_2.setEnabled(False)

    @pyqtSlot(name='on_open_putty')
    def on_open_putty(self):
        if os.name == "nt":
            if MySettings.local.putty_ok:
                func.putty_path(MySettings.device.ip, MySettings.device.user, MySettings.local.path_putty)
            else:
                self.label_9.setText("Putty not found!")
        else:
            os.system("xterm -hold -e 'ssh %s@%s'" % (MySettings.device.user, MySettings.device.ip))

    @pyqtSlot(name='on_path_putty')
    def on_path_putty(self):
        self.set_putty()

    @pyqtSlot(name='set_putty')
    def set_putty(self):
        conf_file = QFileDialog.getOpenFileName()
        if conf_file[0] == "":
            return

        MySettings.local.path_putty = conf_file[0]
        self.lineEdit_10.setText(MySettings.local.path_putty)

    @pyqtSlot(name='on_path_psplash')
    def on_path_psplash(self):
        self.set_psplash()

    @pyqtSlot(name='set_psplash')
    def set_psplash(self):
        psplash_file = QFileDialog.getOpenFileName()
        if psplash_file[0] == "":
            return
        MySettings.project.path_psplash = psplash_file[0]
        self.lineEdit_11.setText(MySettings.project.path_psplash)

    @pyqtSlot(name='on_path_winscp')
    def on_path_winscp(self):
        self.set_winscp()

    @pyqtSlot(name='set_winscp')
    def set_winscp(self):
        conf_file = QFileDialog.getOpenFileName()
        if conf_file[0] == "":
            return

        MySettings.local.path_winscp = conf_file[0]
        self.lineEdit_9.setText(MySettings.local.path_winscp)

    @pyqtSlot(name='on_button_reboot')
    def on_button_reboot(self):
        MySettings.device.file_protocol = protocol_get(self)
        func.scp_reboot(MySettings)
        self.label_9.setText("Reboot command send.")

    @pyqtSlot(name='on_button_poweroff')
    def on_button_poweroff(self):
        MySettings.device.file_protocol = protocol_get(self)
        func.scp_poweroff(MySettings)
        self.label_9.setText("Power off command activate.")

    @pyqtSlot(name='on_button_ts_test')
    def on_button_ts_test(self):
        MySettings.device.file_protocol = protocol_get(self)
        func.scp_ts_test(MySettings)
        self.label_9.setText('Device stopped. TSLIB_TSDEVICE ts_test launched.')

    @pyqtSlot(name='on_button_ts_calibrate')
    def on_button_ts_calibrate(self):
        MySettings.device.file_protocol = protocol_get(self)
        func.scp_ts_calibrate(MySettings)
        self.label_9.setText("Device stopped. TSLIB_TSDEVICE ts_calibrate launched.")

    @pyqtSlot(name='on_button_killall')
    def on_button_killall(self):
        MySettings.device.file_protocol = protocol_get(self)
        func.scp_killall(MySettings)

    @pyqtSlot(name='on_winscp_use')
    def on_winscp_user(self):
        if self.checkBox_3.isChecked():
            self.radioButton.setEnabled(True)
            self.radioButton_2.setEnabled(True)

        elif not self.checkBox.isChecked():
            self.radioButton.setEnabled(False)
            self.radioButton_2.setEnabled(False)
            MySettings.server.sync_files = '0'
            self.radioButton.setChecked(True)

    @pyqtSlot(name='on_button_open')
    def on_button_open(self):
        global SETTINGS_FILE
        conf_file = QFileDialog.getOpenFileName()
        if conf_file[0] == "":
            return

        SETTINGS_FILE = conf_file[0]
        MySettings.save(MySettings)
        MySettings.load(MySettings)
        MySettings.init(MySettings, self)

    @pyqtSlot(name='on_button_apply')
    def on_button_apply(self):
        MySettings.device.user = self.lineEdit_3.text()
        MySettings.device.ip = self.lineEdit_2.text()
        MySettings.device.password = self.lineEdit_4.text()
        MySettings.project.name = self.lineEdit.text()
        MySettings.project.path_local = self.lineEdit_5.text()
        MySettings.server.ip = self.lineEdit_6.text()
        MySettings.server.user = self.lineEdit_7.text()
        MySettings.server.password = self.lineEdit_8.text()
        MySettings.server.path_external = self.lineEdit_12.text()
        if self.radioButton_2.isChecked():
            MySettings.server.sync_files = '1'
        elif self.radioButton.isChecked():
            MySettings.server.sync_files = '0'
        if self.checkBox_3.isChecked():
            MySettings.device.ftp_mode = '1'
        else:
            MySettings.device.ftp_mode = '0'
        MySettings.local.path_winscp = self.lineEdit_9.text()
        MySettings.local.path_putty = self.lineEdit_10.text()
        MySettings.project.path_psplash = self.lineEdit_11.text()
        self.label_9.setText("New configuration applied.")

        # cache saving source history
        fs.cache_save(MyCache.source, MySettings.project.path_local)
        # cache saving project name history
        fs.cache_save(MyCache.project, MySettings.project.name)
        # cache saving device ip history
        fs.cache_save(MyCache.device_ip, MySettings.device.user)
        # cache saving winscp path history
        fs.cache_save(MyCache.winscp, MySettings.local.path_winscp)
        # cache saving putty path history
        fs.cache_save(MyCache.putty, MySettings.local.path_putty)
        # cache saving psplash path history
        fs.cache_save(MyCache.psplash, MySettings.project.path_psplash)

    @pyqtSlot(name='on_path_project')
    def on_path_project(self):
        self.open_file_dialog()

    def open_file_dialog(self):
        path_project = QFileDialog.getExistingDirectory()
        if path_project == "":
            return
        if os.name == "nt":
            path_tmp = fs.path_double_win(path_project)
        else:
            path_tmp = fs.path_double_nix(path_project)

        print('Path changes with SYSTEM requires: \n')
        print('From: %s\nTo: %s\n' % (path_project, path_tmp))
        MySettings.project.name = path_tmp
        self.lineEdit_5.setText(MySettings.project.name)

    @pyqtSlot(name='on_button_reload')
    def on_button_reload(self):
        self.lineEdit.clear()
        self.lineEdit_2.clear()
        self.lineEdit_3.clear()
        self.lineEdit_4.clear()
        self.lineEdit_5.clear()
        self.lineEdit_6.clear()
        self.lineEdit_7.clear()
        self.lineEdit_8.clear()
        self.lineEdit_9.clear()
        self.lineEdit_10.clear()
        self.lineEdit_11.clear()
        self.lineEdit_12.clear()
        MySettings.load(MySettings)
        MySettings.init(MySettings, self)
        self.label_9.setText("Configuration re-init")

    @pyqtSlot(name='on_button_save')
    def on_button_save(self):
        MySettings.device.user = self.lineEdit_3.text()
        MySettings.device.ip = self.lineEdit_2.text()
        MySettings.device.password = self.lineEdit_4.text()
        MySettings.project.name = self.lineEdit.text()
        MySettings.project.path_local = self.lineEdit_5.text()
        MySettings.server.ip = self.lineEdit_6.text()
        MySettings.server.user = self.lineEdit_7.text()
        MySettings.server.password = self.lineEdit_8.text()
        MySettings.server.path_external = self.lineEdit_12.text()
        if self.radioButton_2.isChecked():
            MySettings.server.sync_files = '1'
        elif self.radioButton.isChecked():
            MySettings.server.sync_files = '0'

        if self.checkBox_3.isChecked():
            MySettings.device.ftp_mode = '1'
        else:
            MySettings.device.ftp_mode = '0'
        MySettings.local.path_winscp = self.lineEdit_9.text()
        MySettings.local.path_putty = self.lineEdit_10.text()
        MySettings.project.path_psplash = self.lineEdit_11.text()
        MySettings.save(MySettings)
        self.label_9.setText("Configuration save")

    @pyqtSlot(name='on_button_ping')
    def on_button_ping(self):
        status = func.is_online(MySettings.device.ip)

        if status == 1:
            self.label_9.setText("Device online [%s status: %d]" % (MySettings.device.ip, status))
        elif status == 0:
            self.label_9.setText("Device offline [%s status: %d]" % (MySettings.device.ip, status))

    @pyqtSlot(name='on_button_stop')
    def on_button_stop(self):
        MySettings.device.file_protocol = protocol_get(self)
        func.scp_stop(MySettings)
        self.label_9.setText("Stop command has been sent")

    @pyqtSlot(name='on_button_restart')
    def on_button_restart(self):
        MySettings.device.file_protocol = protocol_get(self)
        func.scp_restart(MySettings)
        self.label_9.setText("Restart command has been sent")

    def on_working_change(self, value):
        if value == 1:
            self.label_9.setText("Working...")
        elif value == 0:
            self.label_9.setText("Firmware is compiled.")
            fs.path_get_firmware(MySettings.project.path_local + "\\Build\\bin\\" + MySettings.project.name + ".bin", self.label_16)
        else:
            self.label_9.setText("Unknown operation.")

    def on_working_change_debug(self, value):
        if value == 1:
            self.label_9.setText("Working...")
        elif value == 0:
            self.label_9.setText("Firmware debug is compiled.")
        else:
            self.label_9.setText("Unknown operation.")

    @pyqtSlot(name='on_button_compile_debug_once')
    def on_button_compile_debug_once(self):
        MySettings.server.compile_mode = True
        if self.comboBox_7.currentText().find('gcc8') == 0:
            MySettings.server.compiler = 'gcc8'
        else:
            MySettings.server.compiler = ''
        self.calc = EProgBar_debug()
        self.calc.working_status_debug.connect(self.on_working_change_debug)
        self.calc.start()

    @pyqtSlot(name='on_button_compile_debug')
    def on_button_compile_debug(self):
        MySettings.server.compile_mode = False
        if self.comboBox_7.currentText().find('gcc8') == 0:
            MySettings.server.compiler = 'gcc8'
        else:
            MySettings.server.compiler = ''
        self.calc = EProgBar_debug()
        self.calc.working_status_debug.connect(self.on_working_change_debug)
        self.calc.start()

    @pyqtSlot(name='on_button_compile_once')
    def on_button_compile_once(self):
        MySettings.server.compile_mode = True
        if self.comboBox_7.currentText().find('gcc8') == 0:
            MySettings.server.compiler = 'gcc8'
        else:
            MySettings.server.compiler = ''
        self.calc = EProgBar()
        self.calc.working_status.connect(self.on_working_change)
        self.calc.start()

    @pyqtSlot(name='on_button_compile')
    def on_button_compile(self):
        if self.comboBox_7.currentText().find('gcc8') == 0:
            MySettings.server.compiler = 'gcc8'
        else:
            MySettings.server.compiler = ''
        MySettings.server.compile_mode = False
        self.calc.working_status.connect(self.on_working_change)
        self.calc.start()

    @pyqtSlot(name='on_button_upload')
    def on_button_upload(self):
        func.scp_upload(MySettings)
        self.label_9.setText("Update without restarting command has been sent")

    @pyqtSlot(name='on_button_auto')
    def on_button_auto(self):
        if self.checkBox_2.isChecked():
            if self.comboBox_7.currentText().find('gcc8') == 0:
                MySettings.server.compiler = 'gcc8'
            else:
                MySettings.server.compiler = ''
            if os.path.exists(Settings.project.path_local):
                func.scp_compile(MySettings, 'release')
            else:
                self.label_9.setText("Project PATH not found. Exiting.")
                print('Project PATH not found. Exiting.')
                return

        MySettings.device.file_protocol = protocol_get(self)

        if self.checkBox.isChecked():
            is_online = func.is_online(MySettings.device.ip, 9999)
            self.label_9.setText("Trying to connect...")
            self.label_9.setText("Connect established.")
            if is_online:
                func.scp_stop(MySettings)
                func.scp_upload(MySettings)
                func.scp_restart(MySettings)
                self.label_9.setText("Auto compile&stop&upload command has been sent")
            else:
                self.label_9.setText("process has been interrupted")
        else:
            func.scp_stop(MySettings)
            func.scp_upload(MySettings)
            func.scp_restart(MySettings)
            self.label_9.setText("Once compile&stop&upload command has been sent")


def main():
    import sys
    fs.cache_create(MyCache.list)
    app = QtWidgets.QApplication(sys.argv)
    app.setStyle('Fusion')
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


def get_value(line, start):
    value = ""
    for i in range(start, len(line)):
        if line[i] == " " and line[i+1] == "'":
            j = i+2
            while line[j] != "'":
                value += line[j]
                j += 1
    return value


def check_value(line):
    new_value = ""
    for i in range(0, len(line)):
        if line[i] != '\n':
            new_value += line[i]
    return new_value


def protocol_get(self):
    if self.comboBox_8.currentText() == 'SCP':
        return str('scp')
    elif self.comboBox_8.currentText() == 'SFTP':
        return str('sftp')


if __name__ == '__main__':
    # init global variables
    MySettings = Settings
    MyCache = Cache_file
    main()
