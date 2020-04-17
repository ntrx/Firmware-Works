# #!/usr/bin/env python

from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtCore import pyqtSlot, QThread, pyqtSignal
from gui import Ui_MainWindow
import os
import subprocess

PROG_NAME = "Firmware Works"
VERSION = "1.0.5"
RELEASE = "beta"

SETTINGS_EMPTY: str = ""
SETTINGS_FILE: str = "settings.py"

# *** Global constants and definitions
# File protocols ( device.file_protocol )
_SFTP_: int = 1
_SCP_: int = 0
# System arch ( device.system )
_NXP_: int = 0
_ATOM_: int = 1
# Sync files ( server.sync_files )
_UPLOAD_FILES_: bool = False
_SYNC_FILES_: bool = True
# Compiler version ( server.compiler )
_GCC_: str = ""
_GCC8_: str = "gcc8"
# Connection type ( local.connection_type )
_WINSCP_PUTTY_: int = 0
_PARAMIKO_: int = 1
_SSH_SCP_SFTP_: int = 2
_LINUX_BUILT_IN_: int = 3
# OS ( local.os )
_WINDOWS_: int = 0
_LINUX_: int = 1
# Build/bin directory
if os.name == "nt":
    _BUILD_BIN_: str = "\\Build\\bin\\"
else:
    _BUILD_BIN_: str = "/Build/bin/"
# *** end of global constants and definitions

import fs
import func
import func_winscp
import func_linux
import func_paramiko


class Cache_file:
    """ Cache files list and functions """
    source: str = "source-history.log"
    project: str = "project-history.log"
    device_ip: str = "device-ip-history.log"
    winscp: str = "winscp-history.log"
    putty: str = "putty-history.log"
    psplash: str = "psplash-history.log"
    list = []

    def init(self):
        """
        Init filenames list

        :return: filename list
        """
        listing = []
        paths = vars(self)
        for item in paths:
            listing.append(str(paths[item]))
        for i in range(3, 9):
            self.list.append(listing[i])

        for file in self.list:
            if not os.path.exists(file):
                fs.cache_create(self.list)


class Settings:
    """ Application configuration  """
    class device:
        """ Embedded device properties """
        user: str = ""                              # Username to login
        password: str = ""                          # Password to login
        ip: str = ""                                # IP address
        file_protocol: int = _SCP_                  # Type of file protocol 1-SFTP or 0-SCP
        system: int = _NXP_                         # 0 - using NXP processors, 1 - using Intem Atom processors

    class server:
        """ Build-server properties """
        user: str = ""                              # Username to login
        password: str = ""                          # Password to login
        ip: str = ""                                # Server IP
        path_external: str = ""                     # PATH to upload sources
        path_executable: str = ""                   # PATH with executable binary
        sync_files: bool = _UPLOAD_FILES_           # Upload files (false), sync files (true)
        compiler: str = _GCC_                       # Type of compiler gcc or gcc8
        compile_mode: bool = False                  # If true then clean object files before compiling (recompiling)

    class project:
        """ Project settings """
        name: str = ""                              # Name of project which has been applied to output binary file
        path_local: str = ""                        # Local PATH of sources
        path_psplash: str = ""                      # Local PATH of psplash file

    class local:
        """ Some miscellaneous properties (local for app) """
        path_winscp: str = ""                       # WinSCP local PATH
        path_putty: str = ""                        # PuTTy local PATH
        winscp_ok: bool = False                     # is WinSCP found
        putty_ok: bool = False                      # is PuTTy found
        connection_type: int = _WINSCP_PUTTY_       # by 0 - winscp+putty / 1 - paramiko / 2 - ssh+scp+sftp / 3 - builtin (linux) apps
        os: int = _WINDOWS_                         # 0 - Windows / 1 - Linux

    def load(self):
        """ Loading configuration file and creating default if not found """
        if not os.path.exists(SETTINGS_FILE):  # Create default configuration file
            print("User settings not found, creating preset file.")
            self.device.user = 'example_user'
            self.device.ip = '127.0.0.1'
            self.device.password = '1111'
            self.project.name = 'sn1111'
            self.project.path_local = 'C:/example_proj'
            self.server.path_external = '/home/root/'
            self.server.path_executable = '/home/root/bin/'
            self.server.ip = '127.0.0.0'
            self.server.user = 'root'
            self.server.password = '1111'
            self.server.sync_files = _UPLOAD_FILES_
            self.local.connection_type = _PARAMIKO_
            self.local.path_winscp = 'C:/example'
            self.local.path_putty = 'C:/example'
            self.project.path_psplash = 'C:/example'
            self.save(self)

        # If find == 0 its our parameter (because all they is starting from 0)
        with open(SETTINGS_FILE) as fp:
            for line in fp:
                if line.find('user') == 0:
                    index = 4
                    self.device.user = func.get_value(line, index)

                if line.find('host') == 0:
                    index = 4
                    self.device.ip = func.get_value(line, index)

                if line.find('secret') == 0:
                    index = 6
                    self.device.password = func.get_value(line, index)

                if line.find('project') == 0:
                    index = 7
                    self.project.name = func.get_value(line, index)

                if line.find('source') == 0:
                    index = 6
                    self.project.path_local = func.get_value(line, index)

                if line.find('global_build_server') == 0:
                    index = 19
                    self.server.ip = func.get_value(line, index)

                if line.find('global_bs_user') == 0:
                    index = 14
                    self.server.user = func.get_value(line, index)

                if line.find('global_bs_secret') == 0:
                    index = 16
                    self.server.password = func.get_value(line, index)

                if line.find('global_bs_dir') == 0:
                    index = 13
                    self.server.path_external = func.get_value(line, index)

                if line.find('path_executable') == 0:
                    index = len('path_executable')
                    self.server.path_executable = func.get_value(line, index)

                if line.find('update') == 0:
                    index = 6
                    tmp_value = int(func.get_value(line, index))
                    if tmp_value == 0:
                        self.server.sync_files = _UPLOAD_FILES_
                    elif tmp_value == 1:
                        self.server.sync_files = _SYNC_FILES_

                if line.find('connection_type') == 0:
                    index = 15
                    self.local.connection_type = int(func.get_value(line, index))

                if line.find('path_scp') == 0:
                    index = 8
                    self.local.path_winscp = func.get_value(line, index)

                if line.find('path_putty') == 0:
                    index = 10
                    self.local.path_putty = func.get_value(line, index)

                if line.find('path_psplash') == 0:
                    index = 12
                    self.project.path_psplash = func.get_value(line, index)
            fp.close()

    def save(self):
        """ Saving configuration file """
        fp = open(SETTINGS_FILE, 'w')
        fp.write("# Auto created settings file. Remember that value is framed by '' \n")
        check = func.check_value(self.device.user)
        fp.write("user = '%s' # user login to device (default: root) \n" % check)
        check = func.check_value(self.device.ip)
        fp.write("host = '%s' # device IP \n" % check)
        check = func.check_value(self.device.password)
        fp.write("secret = '%s' # user pass to device (default: empty) \n" % check)
        check = func.check_value(self.project.name)
        fp.write("project = '%s' # project name (sn4215, sn3307) \n" % check)
        check = func.check_value(self.project.path_local)
        fp.write("source = '%s' # path to project (must contain: Build, Src) \n" % check)
        check = func.check_value(self.server.ip)
        fp.write("global_build_server = '%s' # Build-Server IP  \n" % check)
        check = func.check_value(self.server.user)
        fp.write("global_bs_user = '%s' # Your login to build-server \n" % check)
        check = func.check_value(self.server.password)
        fp.write("global_bs_secret = '%s' # Pass\n" % check)
        check = func.check_value(self.server.path_external)
        fp.write("global_bs_dir = '%s' # uploading directory on build-server\n" % check)
        check = func.check_value(self.server.path_executable)
        fp.write("path_executable = '%s' # executable directory on build-server (if BS built-in to device)\n" % check)
        if self.server.sync_files == _SYNC_FILES_:
            check = 1
        elif self.server.sync_files == _UPLOAD_FILES_:
            check = 0
        fp.write("update = '%d' #  0 - update, 1 - sync \n" % check)
        fp.write("connection_type = '%d' # - 0 - use winSCP+putty, 1 - paramiko, 2 - ssh+scp+sftp, 3 - linux onboard\n" % self.local.connection_type)
        check = func.check_value(self.local.path_winscp)
        fp.write("path_scp = '%s' # - path to WinSCP .com file \n" % check)
        check = func.check_value(self.local.path_putty)
        fp.write("path_putty = '%s' # - path to Putty exe file \n" % check)
        check = func.check_value(self.project.path_psplash)
        fp.write("path_psplash = '%s' # - path to pslpash file\n" % check)
        fp.close()

    def init(self, gui):
        """ Initialize configuration to GUI """
        if os.name == "nt":
            self.local.os = _WINDOWS_
        else:
            self.local.os = _LINUX_

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

        if len(self.server.path_executable) == 0:
            gui.lineEdit_13.setText(SETTINGS_EMPTY)
        else:
            gui.lineEdit_13.setText(self.server.path_executable)

        if self.local.connection_type == _WINSCP_PUTTY_:  # If selected 'winscp + putty'
            gui.comboBox_11.setCurrentIndex(_WINSCP_PUTTY_)
            # Enabling upload or sync radiobutton
            gui.radioButton.setEnabled(True)
            gui.radioButton_2.setEnabled(True)
            # Enabling autorun.sh commands by ssh protocol
            gui.pushButton_11.setEnabled(True)  # killall
            gui.pushButton_2.setEnabled(True)  # restart
            gui.pushButton_5.setEnabled(True)  # stop
            gui.pushButton_4.setEnabled(True)  # only upload
            gui.pushButton.setEnabled(True)  # UPLOAD
            gui.pushButton_13.setEnabled(True)  # calibrate sensor
            gui.pushButton_14.setEnabled(True)  # test sensor
            gui.pushButton_22.setEnabled(True)  # psplash upload
        elif self.local.connection_type == _PARAMIKO_:  # If selected 'paramiko'
            gui.comboBox_11.setCurrentIndex(_PARAMIKO_)
            # Disabling upload or sync radiobutton
            gui.radioButton.setEnabled(False)
            gui.radioButton_2.setEnabled(False)
            # Only upload mode to build-server
            self.server.sync_files = False
            # Disabling autorun.sh commands by ssh protocol
            gui.pushButton_11.setEnabled(False)  # killall
            gui.pushButton_2.setEnabled(False)  # restart
            gui.pushButton_5.setEnabled(False)  # stop
            gui.pushButton_4.setEnabled(False)  # only upload
            gui.pushButton.setEnabled(False)  # UPLOAD
            gui.pushButton_13.setEnabled(False)  # calibrate sensor
            gui.pushButton_14.setEnabled(False)   # test sensor
            gui.pushButton_22.setEnabled(False)  # psplash upload
        elif self.local.connection_type == _SSH_SCP_SFTP_:
            gui.comboBox_11.setCurrentIndex(_SSH_SCP_SFTP_)
        elif self.local.connection_type == _LINUX_BUILT_IN_:
            gui.comboBox_11.setCurrentIndex(_LINUX_BUILT_IN_)

        if self.server.sync_files == _UPLOAD_FILES_:
            gui.radioButton.setChecked(True)
        elif self.server.sync_files == _SYNC_FILES_:
            gui.radioButton_2.setChecked(True)

        if self.local.os == _WINDOWS_:
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

        if self.local.os == _WINDOWS_:
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

        firmware_path = self.project.path_local + _BUILD_BIN_ + self.project.name + ".bin"
        fs.path_get_firmware(firmware_path, gui.label_16)


class EProgBar(QThread):
    working_status = pyqtSignal(int)

    def run(self):
        self.working_status.emit(1)
        if os.path.exists(Settings.project.path_local):
            if MySettings.local.connection_type == _WINSCP_PUTTY_:  # Windows/winSCP
                func_winscp.make(MySettings, 'release')
            elif MySettings.local.connection_type == _PARAMIKO_:  # Paramiko
                func_paramiko.make(MySettings, 'release')
            elif MySettings.local.connection_type == _SSH_SCP_SFTP_:
                pass
            elif MySettings.local.connection_type == _LINUX_BUILT_IN_:
                pass
        else:
            print('Project PATH not found.')
        self.working_status.emit(0)


class EProgBar_debug(QThread):
    working_status_debug = pyqtSignal(int)

    def run(self):
        self.working_status_debug.emit(1)
        if os.path.exists(Settings.project.path_local):
            if MySettings.local.connection_type == _WINSCP_PUTTY_:
                func_winscp.make(MySettings, 'debug')
            elif MySettings.local.connection_type == _PARAMIKO_:
                func_paramiko.make(MySettings, 'debug')
            elif MySettings.local.connection_type == _SSH_SCP_SFTP_:
                pass
            elif MySettings.local.connection_type == _LINUX_BUILT_IN_:
                pass
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

        # self.label_9.setStyleSheet('background-color: red') for future
        MySettings.load(MySettings)
        MyCache.init(MyCache)
        # init text labels and 'end' panel
        MySettings.init(MySettings, self)

        if MySettings.local.os == _WINDOWS_:
            pass
        elif MySettings.local.os == _LINUX_:
            # Tab: External
            self.tabWidget.setTabEnabled(2, False)
            # Button: open with winSCP
            self.pushButton_25.setVisible(False)
            # Button: open with Putty
            self.pushButton_26.setText("open with xterm")
            # Button: putty
            self.pushButton_17.setText("xterm")
            # Button: winSCP
            self.pushButton_24.setVisible(False)

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
        self.pushButton_27.clicked.connect(self.on_button_rmdir)

        # tool buttons
        self.toolButton_2.clicked.connect(self.on_path_project)
        self.toolButton_3.clicked.connect(self.on_path_winscp)
        self.toolButton_4.clicked.connect(self.on_path_putty)
        self.toolButton_5.clicked.connect(self.on_path_psplash)

        # comboboxes
        self.comboBox.currentIndexChanged.connect(self.on_project_change)
        self.comboBox_3.currentIndexChanged.connect(self.on_source_change)
        self.comboBox_2.currentIndexChanged.connect(self.on_device_ip_change)
        self.comboBox_4.currentIndexChanged.connect(self.on_winscp_change)
        self.comboBox_5.currentIndexChanged.connect(self.on_putty_change)
        self.comboBox_6.currentIndexChanged.connect(self.on_psplash_change)
        self.comboBox_10.currentIndexChanged.connect(self.on_system_change)
        self.comboBox_11.currentIndexChanged.connect(self.on_connection_type_change)

        # action menu
        self.actionOpen_2.triggered.connect(self.on_button_open)
        self.actionEdit.triggered.connect(self.on_button_edit)
        self.actionPower_off.triggered.connect(self.on_button_poweroff)
        self.actionReboot.triggered.connect(self.on_button_reboot)
        self.actionReload.triggered.connect(self.on_button_reload)
        self.actionSave.triggered.connect(self.on_button_save)
        self.actionRemove.triggered.connect(self.on_act_remove)

    @pyqtSlot(name='on_button_rmdir')
    def on_button_rmdir(self):
        if MySettings.local.connection_type == _WINSCP_PUTTY_:
            func_winscp.rmdir(MySettings)
            self.label_9.setText("SENT: remove external source directory storage.")
        elif MySettings.local.connection_type == _PARAMIKO_:
            func_paramiko.rmdir(MySettings)
            self.label_9.setText("SENT: remove external source directory storage.")
        elif MySettings.local.connection_type == _SSH_SCP_SFTP_:
            func_linux.rmdir(MySettings)
            self.label_9.setText("SENT: remove external source directory storage.")
        elif MySettings.local.connection_type == _LINUX_BUILT_IN_:
            pass
            self.label_9.setText("Remove local source directory storage.")

    # Opening Build Server in Putty or Xterm
    @pyqtSlot(name='on_button_bs_putty')
    def on_button_bs_putty(self):
        if MySettings.local.connection_type == _WINSCP_PUTTY_:
            if MySettings.local.putty_ok:
                func_winscp.putty_path(MySettings.server.ip, MySettings.server.user, MySettings.local.path_putty)
            else:
                self.label_9.setText("Putty not found!")
        elif MySettings.local.connection_type == _PARAMIKO_ and MySettings.local.os == _WINDOWS_:
            if MySettings.local.putty_ok:
                func_winscp.putty_path(MySettings.server.ip, MySettings.server.user, MySettings.local.path_putty)
            else:
                self.label_9.setText("Putty not found!")
        elif MySettings.local.connection_type == _SSH_SCP_SFTP_ and MySettings.local.os == _LINUX_:
            os.system("xterm -hold -e 'ssh %s@%s'" % (MySettings.server.user, MySettings.server.ip))
        else:
            self.label_9.setText("Not compatible setup, try install Putty or Xterm!")

    # Opening Build Server in WinSCP
    @pyqtSlot(name='on_button_bs_winscp')
    def on_button_bs_winscp(self):
        if MySettings.local.os == _WINDOWS_:
            winscp_exe = MySettings.local.path_winscp.replace("com", "exe")
            MySettings.device.file_protocol = func.protocol_get(self)
            command = ("sftp://%s:%s@%s/" % (MySettings.server.user, MySettings.server.password, MySettings.server.ip))
            func_winscp.command(command, winscp_exe)
        elif MySettings.local.os == _LINUX_:
            self.label_9.setText("Not supported!")

    # Opening device in WinSCP by SCP or SFTP protocol
    @pyqtSlot(name='on_button_winscp')
    def on_button_winscp(self):
        command = ""
        if MySettings.local.os == _WINDOWS_:
            winscp_exe = MySettings.local.path_winscp.replace("com", "exe")
            MySettings.device.file_protocol = func.protocol_get(self)
            if MySettings.device.file_protocol == _SFTP_:
                command = ("sftp://%s:%s@%s/" % (MySettings.device.user, MySettings.device.password, MySettings.device.ip))
            elif MySettings.device.file_protocol == _SCP_:
                command = ("scp://%s@%s:%s/" % (MySettings.device.user, MySettings.device.ip, MySettings.device.password))
            func_winscp.command(command, winscp_exe)
        else:
            self.label_9.setText("Not supported!")

    # Delete firmware binary file on local storage
    @pyqtSlot(name='on_act_remove')
    def on_act_remove(self):
        dest_path = MySettings.project.path_local + _BUILD_BIN_ + MySettings.project.name + ".bin"
        if os.path.exists(dest_path):
            os.remove(dest_path)
            self.label_9.setText("Firmware remove command.")
        else:
            self.label_9.setText("Nothing to remove, firmware not found.")

    # Performs make clean
    @pyqtSlot(name='on_button_clean')
    def on_button_clean(self):
        MySettings.device.file_protocol = func.protocol_get(self)
        if MySettings.local.connection_type == _WINSCP_PUTTY_:
            func_winscp.clean(MySettings)
            self.label_9.setText("SENT: clean firmware on remote server.")
        elif MySettings.local.connection_type == _PARAMIKO_:
            func_paramiko.clean(MySettings)
            self.label_9.setText("SENT: clean firmware on remote server.")
        elif MySettings.local.connection_type == _SSH_SCP_SFTP_:
            self.label_9.setText("SENT: clean firmware on remote server.")
            pass
        elif MySettings.local.connection_type == _LINUX_BUILT_IN_:
            self.label_9.setText("Localy clean firmware.")
            pass

    # Toggle sync files
    @pyqtSlot(name='on_radioButton_sync_mode')
    def on_radioButton_sync_mode(self):
        MySettings.server.sync_files = _SYNC_FILES_

    # Toggle upload files
    @pyqtSlot(name='on_radioButton_upload_mode')
    def on_radioButton_upload_mode(self):
        MySettings.server.sync_files = _UPLOAD_FILES_

    # Uploading psplash file to device
    @pyqtSlot(name='on_button_psplash')
    def on_button_psplash(self):
        if func.is_online(MySettings.device.ip):
            MySettings.device.file_protocol = func.protocol_get(self)
            if MySettings.local.connection_type == _WINSCP_PUTTY_:
                func_winscp.psplash_upload(MySettings, self.label_9)
            elif MySettings.local.connection_type == _PARAMIKO_:
                pass
            elif MySettings.local.connection_type == _SSH_SCP_SFTP_:
                func_linux.psplash_upload(MySettings, self.label_9)
            elif MySettings.local.connection_type == _LINUX_BUILT_IN_:
                pass
        else:
            self.label_9.setText("Host is unreachable")

    # If psplash path has been changed
    @pyqtSlot(name='on_psplash_change')
    def on_psplash_change(self):
        self.lineEdit_11.setText(self.comboBox_6.currentText())

    # Checking firmware outdate
    @pyqtSlot(name='on_button_outdated')
    def on_button_outdated(self):
        if func.is_online(MySettings.device.ip):
            MySettings.device.file_protocol = func.protocol_get(self)
            if MySettings.local.connection_type == _WINSCP_PUTTY_:
                pass
            elif MySettings.local.connection_type == _PARAMIKO_:
                func_paramiko.detect_outdated_firmware(MySettings, self.label_9)
            elif MySettings.local.connection_type == _SSH_SCP_SFTP_:
                pass
            elif MySettings.local.connection_type == _LINUX_BUILT_IN_:
                pass
        else:
            self.label_9.setText('Host is unreachable')

    # Detect firmware outdate
    @pyqtSlot(name='on_button_detect')
    def on_button_detect(self):
        if func.is_online(MySettings.device.ip):
            MySettings.device.file_protocol = func.protocol_get(self)
            if MySettings.local.connection_type == _WINSCP_PUTTY_:
                pass
            elif MySettings.local.connection_type == _PARAMIKO_:
                func_paramiko.detect_project(MySettings, self.label_9)
            elif MySettings.local.connection_type == _SSH_SCP_SFTP_:
                pass
            elif MySettings.local.connection_type == _LINUX_BUILT_IN_:
                pass
        else:
            self.label_9.setText('Host is unreachable')

    # OPTIONS: Clear cache (history files)
    @pyqtSlot(name='on_button_clear_cache')
    def on_button_clear_cache(self):
        fs.cache_create(MyCache.list)
        self.on_button_apply()
        self.label_9.setText("Cached information has been clear.")

    # OPTIONS: edit settings
    @pyqtSlot(name='on_button_edit')
    def on_button_edit(self):
        if MySettings.local.os == _WINDOWS_:
            CREATE_NO_WINDOW = 0x08000000
            return subprocess.Popen("notepad %s" % SETTINGS_FILE, creationflags=CREATE_NO_WINDOW)
        elif MySettings.local.os == _LINUX_:
            os.system("xdg-open %s" % SETTINGS_FILE)

    # OPTIONS: winscp path changed
    @pyqtSlot(name='on_winscp_change')
    def on_winscp_change(self):
        self.lineEdit_9.setText(self.comboBox_4.currentText())

    # OPTIONS: device ip changed
    @pyqtSlot(name='on_device_ip_change')
    def on_device_ip_change(self):
        self.lineEdit_2.setText(func.check_value(self.comboBox_2.currentText()))

    # OPTIONS: putty path changed
    @pyqtSlot(name='on_putty_change')
    def on_putty_change(self):
        self.lineEdit_10.setText(self.comboBox_5.currentText())

    # OPTIONS: sources path changed
    @pyqtSlot(name='on_source_change')
    def on_source_change(self):
        self.lineEdit_5.setText(self.comboBox_3.currentText())

    # OPTIONS: project name changed
    @pyqtSlot(name='on_project_change')
    def on_project_change(self):
        self.lineEdit.setText(self.comboBox.currentText())

    # OPTION: connection type changed
    @pyqtSlot(name='on_connection_type_change')
    def on_connection_type_change(self):
        MySettings.local.connection_type = int(self.comboBox_11.currentIndex())
        self.comboBox_11.setCurrentIndex(int(MySettings.local.connection_type))

    # OPTIONS: arch changed
    @pyqtSlot(name='on_system_change')
    def on_system_change(self):
        if self.comboBox_10.currentIndex() == 0:  # NXP iMX6(QP)
            Settings.device.system = _NXP_
            self.comboBox_10.setCurrentIndex(0)
            self.comboBox_7.setEnabled(True)
            self.comboBox_8.setEnabled(True)
            # Enabling autorun.sh scripts and project detecting
            self.pushButton_12.setEnabled(True)
            self.pushButton_11.setEnabled(True)
            self.pushButton_2.setText("restart")
            self.pushButton_5.setEnabled(True)
            # Enabling sensor functions and upload firmware/psplash
            self.pushButton_14.setEnabled(True)
            self.pushButton_13.setEnabled(True)
            self.pushButton_22.setEnabled(True)
            self.pushButton_4.setEnabled(True)
            self.pushButton.setEnabled(True)
            self.checkBox.setEnabled(True)
            self.checkBox_2.setEnabled(True)
            # Enabling executable path line
            self.lineEdit_13.setEnabled(True)
            self.label_20.setEnabled(True)
        elif self.comboBox_10.currentIndex() == 1:  # Intel Atom
            Settings.device.system = _ATOM_
            self.comboBox_10.setCurrentIndex(1)
            # Only SFTP protocol there
            self.comboBox_8.setCurrentIndex(1)
            self.comboBox_8.setEnabled(False)
            # Only gcc there
            self.comboBox_7.setCurrentIndex(0)
            self.comboBox_7.setEnabled(False)
            # Disabling autorun.sh scripts and project detecting
            self.pushButton_12.setEnabled(False)
            self.pushButton_11.setEnabled(False)
            self.pushButton_2.setText("run")
            self.pushButton_5.setEnabled(False)
            # Disabling sensor functions and upload firmware/psplash
            self.pushButton_14.setEnabled(False)
            self.pushButton_13.setEnabled(False)
            self.pushButton_22.setEnabled(False)
            self.pushButton_4.setEnabled(False)
            self.pushButton.setEnabled(False)
            self.checkBox.setEnabled(False)
            self.checkBox_2.setEnabled(False)
            # Disabling executable path line
            self.lineEdit_13.setEnabled(False)
            self.label_20.setEnabled(False)

    # Opening device in putty
    @pyqtSlot(name='on_open_putty')
    def on_open_putty(self):
        if MySettings.local.connection_type == _WINSCP_PUTTY_:
            if MySettings.local.putty_ok:
                func_winscp.putty_path(MySettings.server.ip, MySettings.server.user, MySettings.local.path_putty)
            else:
                self.label_9.setText("Putty not found!")
        elif MySettings.local.connection_type == _PARAMIKO_ and MySettings.local.os == _WINDOWS_:
            if MySettings.local.putty_ok:
                func_winscp.putty_path(MySettings.device.ip, MySettings.device.user, MySettings.local.path_putty)
            else:
                self.label_9.setText("Putty not found!")
        elif MySettings.local.connection_type == _SSH_SCP_SFTP_ and MySettings.local.os == _LINUX_:
            os.system("xterm -hold -e 'ssh %s@%s'" % (MySettings.device.user, MySettings.device.ip))
        else:
            self.label_9.setText("Not compatible setup, try install Putty or Xterm!")

    # OPTION: set putty path
    @pyqtSlot(name='on_path_putty')
    def on_path_putty(self):
        self.set_putty()

    # HANDLER: set putty path
    @pyqtSlot(name='set_putty')
    def set_putty(self):
        conf_file = QFileDialog.getOpenFileName(filter="PuTTy.exe")
        if conf_file[0] == "":
            return

        MySettings.local.path_putty = conf_file[0]
        self.lineEdit_10.setText(MySettings.local.path_putty)

    # OPTION: set psplash path
    @pyqtSlot(name='on_path_psplash')
    def on_path_psplash(self):
        self.set_psplash()

    # HANDLER: set psplash path
    @pyqtSlot(name='set_psplash')
    def set_psplash(self):
        psplash_file = QFileDialog.getOpenFileName(filter="psplash.*")
        if psplash_file[0] == "":
            return
        MySettings.project.path_psplash = psplash_file[0]
        self.lineEdit_11.setText(MySettings.project.path_psplash)

    # OPTION: set winscp path
    @pyqtSlot(name='on_path_winscp')
    def on_path_winscp(self):
        self.set_winscp()

    # HANDLER: set winscp path
    @pyqtSlot(name='set_winscp')
    def set_winscp(self):
        conf_file = QFileDialog.getOpenFileName(filter="WinSCP.*")
        if conf_file[0] == "":
            return

        MySettings.local.path_winscp = conf_file[0]
        self.lineEdit_9.setText(MySettings.local.path_winscp)

    # Reboot device
    @pyqtSlot(name='on_button_reboot')
    def on_button_reboot(self):
        MySettings.device.file_protocol = func.protocol_get(self)
        if MySettings.local.connection_type == _WINSCP_PUTTY_:
            func_winscp.reboot(MySettings)
        elif MySettings.local.connection_type == _PARAMIKO_:
            func_paramiko.reboot(MySettings)
        elif MySettings.local.connection_type == _SSH_SCP_SFTP_:
            func_linux.reboot(MySettings)
        elif MySettings.local.connection_type == _LINUX_BUILT_IN_:
            pass
        self.label_9.setText("SENT: reboot command.")

    # Shutdown device
    @pyqtSlot(name='on_button_poweroff')
    def on_button_poweroff(self):
        MySettings.device.file_protocol = func.protocol_get(self)
        if MySettings.local.connection_type == _WINSCP_PUTTY_:
            func_winscp.poweroff(MySettings)
        elif MySettings.local.connection_type == _PARAMIKO_:
            func_paramiko.poweroff(MySettings)
        elif MySettings.local.connection_type == _SSH_SCP_SFTP_:
            func_linux.poweroff(MySettings)
        elif MySettings.local.connection_type == _LINUX_BUILT_IN_:
            pass
        self.label_9.setText("SENT: shutdown command.")

    # Touchscreen calibration test
    @pyqtSlot(name='on_button_ts_test')
    def on_button_ts_test(self):
        MySettings.device.file_protocol = func.protocol_get(self)
        if MySettings.local.connection_type == _WINSCP_PUTTY_:
            func_winscp.ts_test(MySettings)
        elif MySettings.local.connection_type == _PARAMIKO_:
            func_paramiko.ts_test(MySettings)
        elif MySettings.local.connection_type == _SSH_SCP_SFTP_:
            func_linux.ts_test(MySettings)
        elif MySettings.local.connection_type == _LINUX_BUILT_IN_:
            pass
        self.label_9.setText('Device stopped. TSLIB_TSDEVICE ts_test launched.')

    # Touchscreen calibration app
    @pyqtSlot(name='on_button_ts_calibrate')
    def on_button_ts_calibrate(self):
        MySettings.device.file_protocol = func.protocol_get(self)
        if MySettings.local.connection_type == _WINSCP_PUTTY_:
            func_winscp.ts_calibrate(MySettings)
        elif MySettings.local.connection_type == _PARAMIKO_:
            func_paramiko.ts_calibrate(MySettings)
        elif MySettings.local.connection_type == _SSH_SCP_SFTP_:
            func_linux.ts_calibrate(MySettings)
        elif MySettings.local.connection_type == _LINUX_BUILT_IN_:
            pass
        self.label_9.setText("Device stopped. TSLIB_TSDEVICE ts_calibrate launched.")

    # Device killall command (for firmware and autorun.sh)
    @pyqtSlot(name='on_button_killall')
    def on_button_killall(self):
        MySettings.device.file_protocol = func.protocol_get(self)
        if MySettings.local.connection_type == _WINSCP_PUTTY_:
            func_winscp.killall(MySettings)
        elif MySettings.local.connection_type == _PARAMIKO_:
            func_paramiko.killall(MySettings)
        elif MySettings.local.connection_type == _SSH_SCP_SFTP_:
            func_linux.killall(MySettings)
        elif MySettings.local.connection_type == _LINUX_BUILT_IN_:
            pass
        self.label_9.setText("SENT: killall command for %s.bin and autorun.sh" % MySettings.project.name)

    # Using winscp option
    @pyqtSlot(name='on_winscp_use')
    def on_winscp_user(self):
        if self.comboBox_11.currentIndex() == _WINSCP_PUTTY_:
            self.radioButton.setEnabled(True)
            self.radioButton_2.setEnabled(True)
        elif self.comboBox_11.currentIndex() == _PARAMIKO_:
            self.radioButton.setEnabled(False)
            self.radioButton_2.setEnabled(False)
            MySettings.server.sync_files = _UPLOAD_FILES_
            self.radioButton.setChecked(True)
        elif self.comboBox_11.currentIndex() == _SSH_SCP_SFTP_:
            pass
        elif self.comboBox_11.currentIndex() == _LINUX_BUILT_IN_:
            pass

    # Open settings file
    @pyqtSlot(name='on_button_open')
    def on_button_open(self):
        global SETTINGS_FILE
        conf_file = QFileDialog.getOpenFileName(filter=SETTINGS_FILE)
        if conf_file[0] == "":
            return

        SETTINGS_FILE = conf_file[0]
        MySettings.save(MySettings)
        MySettings.load(MySettings)
        MySettings.init(MySettings, self)

    # OPTION: Applying new configuration
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
            MySettings.server.sync_files = _SYNC_FILES_
        elif self.radioButton.isChecked():
            MySettings.server.sync_files = _UPLOAD_FILES_
        MySettings.local.connection_type = self.comboBox_11.currentIndex()
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

    # BUTTON: opening sources path
    @pyqtSlot(name='on_path_project')
    def on_path_project(self):
        self.open_file_dialog()

    # HANDLER: opening sources path
    def open_file_dialog(self):
        path_tmp = ""
        path_project = QFileDialog.getExistingDirectory()
        if path_project == "":
            return
        if MySettings.local.os == _WINDOWS_:
            path_tmp = fs.path_double_win(path_project)
        elif MySettings.local.os == _LINUX_:
            path_tmp = path_project

        print('Path changes with SYSTEM requires: \n')
        print('From: %s\nTo: %s\n' % (path_project, path_tmp))
        MySettings.project.name = path_tmp
        self.lineEdit_5.setText(MySettings.project.name)

    # OPTION: reload configuration from file
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

    # OPTION: save configuration to file
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
            MySettings.server.sync_files = _SYNC_FILES_
        elif self.radioButton.isChecked():
            MySettings.server.sync_files = _UPLOAD_FILES_

        MySettings.local.connection_type = int(self.comboBox_11.currentIndex())
        MySettings.local.path_winscp = self.lineEdit_9.text()
        MySettings.local.path_putty = self.lineEdit_10.text()
        MySettings.project.path_psplash = self.lineEdit_11.text()
        MySettings.save(MySettings)
        self.label_9.setText("Configuration save")

    # Ping device
    @pyqtSlot(name='on_button_ping')
    def on_button_ping(self):
        status = func.is_online(MySettings.device.ip)
        if status == 1:
            self.label_9.setText("Device online [%s status: %d]" % (MySettings.device.ip, status))
        elif status == 0:
            self.label_9.setText("Device offline [%s status: %d]" % (MySettings.device.ip, status))

    # BUTTON: stop command for autorun.sh
    @pyqtSlot(name='on_button_stop')
    def on_button_stop(self):
        MySettings.device.file_protocol = func.protocol_get(self)
        if MySettings.local.connection_type == _WINSCP_PUTTY_:
            func_winscp.stop(MySettings)
        elif MySettings.local.connection_type == _PARAMIKO_:
            func_paramiko.stop(MySettings)
        elif MySettings.local.connection_type == _SSH_SCP_SFTP_:
            func_linux.stop(MySettings)
        elif MySettings.local.connection_type == _LINUX_BUILT_IN_:
            pass
        self.label_9.setText("SENT: stop command.")

    # BUTTON: restart command for autorun.sh
    @pyqtSlot(name='on_button_restart')
    def on_button_restart(self):
        MySettings.device.file_protocol = func.protocol_get(self)
        if MySettings.local.connection_type == _WINSCP_PUTTY_:
            func_winscp.restart(MySettings)
        elif MySettings.local.connection_type == _PARAMIKO_:
            func_paramiko.restart(MySettings)
        elif MySettings.local.connection_type == _SSH_SCP_SFTP_:
            func_linux.restart(MySettings)
        elif MySettings.local.connection_type == _LINUX_BUILT_IN_:
            pass
        self.label_9.setText("SENT: restart command.")

    # Thread handler for firmware compiling
    def on_working_change(self, value):
        if value == 1:
            self.label_9.setText("Working...")
        elif value == 0:
            self.label_9.setText("Firmware is compiled.")
            fs.path_get_firmware(MySettings.project.path_local + _BUILD_BIN_ + MySettings.project.name + ".bin", self.label_16)
        else:
            self.label_9.setText("Unknown operation.")

    # Thread handler for firmware compiling debug version
    def on_working_change_debug(self, value):
        if value == 1:
            self.label_9.setText("Working...")
        elif value == 0:
            self.label_9.setText("Firmware debug is compiled.")
            fs.path_get_firmware(MySettings.project.path_local + _BUILD_BIN_ + MySettings.project.name + ".bin",  self.label_16)
        else:
            self.label_9.setText("Unknown operation.")

    @pyqtSlot(name='on_button_compile_debug_once')
    def on_button_compile_debug_once(self):
        MySettings.server.compile_mode = True
        if self.comboBox_7.currentText().find('gcc8') == 0:
            MySettings.server.compiler = _GCC8_
        else:
            MySettings.server.compiler = _GCC_
        self.calc = EProgBar_debug()
        self.calc.working_status_debug.connect(self.on_working_change_debug)
        self.calc.start()

    @pyqtSlot(name='on_button_compile_debug')
    def on_button_compile_debug(self):
        MySettings.server.compile_mode = False
        if self.comboBox_7.currentText().find('gcc8') == 0:
            MySettings.server.compiler = _GCC8_
        else:
            MySettings.server.compiler = _GCC_
        self.calc = EProgBar_debug()
        self.calc.working_status_debug.connect(self.on_working_change_debug)
        self.calc.start()

    @pyqtSlot(name='on_button_compile_once')
    def on_button_compile_once(self):
        MySettings.server.compile_mode = True
        if self.comboBox_7.currentText().find('gcc8') == 0:
            MySettings.server.compiler = _GCC8_
        else:
            MySettings.server.compiler = _GCC_
        self.calc = EProgBar()
        self.calc.working_status.connect(self.on_working_change)
        self.calc.start()

    @pyqtSlot(name='on_button_compile')
    def on_button_compile(self):
        if self.comboBox_7.currentText().find('gcc8') == 0:
            MySettings.server.compiler = _GCC8_
        else:
            MySettings.server.compiler = _GCC_
        MySettings.server.compile_mode = False
        self.calc.working_status.connect(self.on_working_change)
        self.calc.start()

    @pyqtSlot(name='on_button_upload')
    def on_button_upload(self):
        if MySettings.local.connection_type == _WINSCP_PUTTY_:
            func_winscp.upload(MySettings)
        elif MySettings.local.connection_type == _PARAMIKO_:
            func_paramiko.upload(MySettings)
        elif MySettings.local.connection_type == _SSH_SCP_SFTP_:
            func_linux.upload(MySettings)
        elif MySettings.local.connection_type == _LINUX_BUILT_IN_:
            pass
        self.label_9.setText("SENT: shadow upload command.")

    @pyqtSlot(name='on_button_auto')
    def on_button_auto(self):
        MySettings.device.file_protocol = func.protocol_get(self)
        if self.checkBox_2.isChecked():
            if self.comboBox_7.currentIndex() == 0:
                MySettings.server.compiler = _GCC_
            elif self.comboBox_7.currentIndex() == 1:
                MySettings.server.compiler = _GCC8_
            if os.path.exists(Settings.project.path_local):
                if MySettings.local.connection_type == _WINSCP_PUTTY_:
                    func_winscp.make(MySettings, 'release')
                elif MySettings.local.connection_type == _PARAMIKO_:
                    func_paramiko.make(MySettings, 'release')
                elif MySettings.local.connection_type == _SSH_SCP_SFTP_:
                    func_linux.make(MySettings, 'release')
                elif MySettings.local.connection_type == _LINUX_BUILT_IN_:
                    pass
            else:
                self.label_9.setText("Project PATH not found. Exiting.")
                print('Project PATH not found. Exiting.')
                return

        if self.checkBox.isChecked():
            is_online = func.is_online(MySettings.device.ip, 1)
            self.label_9.setText("Trying to connect...")
            self.label_9.setText("Connect established.")
            if is_online:
                if MySettings.local.connection_type == _WINSCP_PUTTY_:
                    func_winscp.stop(MySettings)
                    func_winscp.upload(MySettings)
                    func_winscp.restart(MySettings)
                elif MySettings.local.connection_type == _PARAMIKO_:
                    func_paramiko.stop(MySettings)
                    func_paramiko.upload(MySettings)
                    func_paramiko.restart(MySettings)
                elif MySettings.local.connection_type == _SSH_SCP_SFTP_:
                    func_linux.stop(MySettings)
                    func_linux.upload(MySettings)
                    func_linux.restart(MySettings)
                elif MySettings.local.connection_type == _LINUX_BUILT_IN_:
                    pass
                self.label_9.setText("Auto compile&stop&upload command has been sent")
            else:
                self.label_9.setText("process has been interrupted")
        else:
            if MySettings.local.connection_type == _WINSCP_PUTTY_:
                func_winscp.stop(MySettings)
                func_winscp.upload(MySettings)
                func_winscp.restart(MySettings)
            elif MySettings.local.connection_type == _PARAMIKO_:
                func_paramiko.stop(MySettings)
                func_paramiko.upload(MySettings)
                func_paramiko.restart(MySettings)
            elif MySettings.local.connection_type == _SSH_SCP_SFTP_:
                func_linux.stop(MySettings)
                func_linux.upload(MySettings)
                func_linux.restart(MySettings)
            elif MySettings.local.connection_type == _LINUX_BUILT_IN_:
                pass
            self.label_9.setText("Once compile&stop&upload command has been sent")


def main():
    import sys
    fs.cache_create(MyCache.list)
    app = QtWidgets.QApplication(sys.argv)
    app.setStyle('Fusion')
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    # init global variables
    MySettings = Settings
    MyCache = Cache_file
    main()
