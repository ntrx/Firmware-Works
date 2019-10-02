# #!/usr/bin/env python

# python 3.7 last version 12:30 03072019
# use libs: PIP: pyqt5->pyiuc5 (for GUI
# pyinstaller (for executable

from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtCore import pyqtSlot, QThread, pyqtSignal
from gui import Ui_MainWindow
import func
import paramiko
import os
import subprocess
import fs


SETTINGS_USER: str = ""
SETTINGS_HOST: str = ""
SETTINGS_SECRET: str = ""
SETTINGS_PROJECT: str = ""
SETTINGS_SOURCE: str = ""
SETTINGS_GLOB_BLD_SRV: str = ""
SETTINGS_GLOB_BS_USR: str = ""
SETTINGS_GLOB_BS_SCRT: str = ""
SETTINGS_UPDATE: str = ""
SETTINGS_FTP_MODE: str = ""
PATH_WINSCP: str = ""
PATH_PUTTY: str = ""
PATH_PSPLASH: str = ""

PATH_WINSCP_OK: bool = False
PATH_PUTTY_OK: bool = False

SETTINGS_EMPTY: str = ""
SETTINGS_FILE: str = "settings.py"
SETTINGS_SOURCE_HISTORY = "source-history.log"
SETTINGS_PROJECT_HISTORY = "project-history.log"
SETTINGS_DEVICE_IP_HISTORY = "device-ip-history.log"
SETTINGS_WINSCP_HISTORY = "winscp-history.log"
SETTINGS_PUTTY_HISTORY = "putty-history.log"
SETTINGS_PSPLASH_HISTORY = "psplash-history.log"
cache_files = [SETTINGS_DEVICE_IP_HISTORY, SETTINGS_PROJECT_HISTORY, SETTINGS_PUTTY_HISTORY, SETTINGS_WINSCP_HISTORY, SETTINGS_SOURCE_HISTORY, SETTINGS_PSPLASH_HISTORY]


class MySFTPClient(paramiko.SFTPClient):
    def put_dir(self, source, target):
        for item in os.listdir(source):
            if os.path.isfile(os.path.join(source, item)):
                self.put(os.path.join(source, item), '%s/%s' % (target, item))
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
        func.scp_compile(SETTINGS_SOURCE, SETTINGS_GLOB_BS_USR, SETTINGS_GLOB_BS_SCRT, SETTINGS_PROJECT, SETTINGS_UPDATE, 'release')
        self.working_status.emit(0)


class EProgBar_debug(QThread):
    working_status_debug = pyqtSignal(int)

    def run(self):
        self.working_status_debug.emit(1)
        func.scp_compile(SETTINGS_SOURCE, SETTINGS_GLOB_BS_USR, SETTINGS_GLOB_BS_SCRT, SETTINGS_PROJECT, SETTINGS_UPDATE, 'debug')
        self.working_status_debug.emit(0)


class MainWindow(QtWidgets. QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        # gui init
        super(MainWindow, self).__init__(parent)
        QtWidgets.QMainWindow.__init__(self)
        self.setupUi(self)

        # self.label_9.setStyleSheet('background-color: red') for future
        settings_load()
        # init text labels and 'end' panel
        self.settings_init()

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

        # action menu
        self.actionOpen_2.triggered.connect(self.on_button_open)
        self.actionEdit.triggered.connect(self.on_button_edit)
        self.actionPower_off.triggered.connect(self.on_button_poweroff)
        self.actionReboot.triggered.connect(self.on_button_reboot)
        self.actionReload.triggered.connect(self.on_button_reload)
        self.actionSave.triggered.connect(self.on_button_save)

    @pyqtSlot(name='on_button_psplash')
    def on_button_psplash(self):
        if func.is_online(SETTINGS_HOST):
            func.scp_psplash_upload(SETTINGS_HOST, SETTINGS_USER, SETTINGS_SECRET, fs.path_double_win(PATH_PSPLASH), self.label_9)
        else:
            self.label_9.setText("Host is unreachable")

    @pyqtSlot(name='on_psplash_change')
    def on_psplash_change(self):
        self.lineEdit_11.setText(self.comboBox_6.currentText())

    @pyqtSlot(name='on_button_outdated')
    def on_button_outdated(self):
        if func.is_online(SETTINGS_HOST):
            func.scp_detect_outdated_firmware(SETTINGS_HOST, SETTINGS_USER, SETTINGS_SECRET, SETTINGS_PROJECT, SETTINGS_SOURCE, self.label_9)
        else:
            self.label_9.setText('Host is unreachable')

    @pyqtSlot(name='on_button_detect')
    def on_button_detect(self):
        if func.is_online(SETTINGS_HOST):
            func.scp_detect_project(SETTINGS_HOST, SETTINGS_USER, SETTINGS_SECRET, self.label_9)
        else:
            self.label_9.setText('Host is unreachable')

    @pyqtSlot(name='on_button_clear_cache')
    def on_button_clear_cache(self):
        for file in cache_files:
            f = open(file, "w")
            f.write("")
            f.close()

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
        self.lineEdit_2.setText(self.comboBox_2.currentText())
        
    @pyqtSlot(name='on_putty_change')
    def on_putty_change(self):
        self.lineEdit_10.setText(self.comboBox_5.currentText())
        
    @pyqtSlot(name='on_source_change')
    def on_source_change(self):
        self.lineEdit_5.setText(self.comboBox_3.currentText())

    @pyqtSlot(name='on_project_change')
    def on_project_change(self):
        self.lineEdit.setText(self.comboBox.currentText())

    @pyqtSlot(name='on_open_putty')
    def on_open_putty(self):
        if os.name == "nt":
            if PATH_PUTTY_OK:
                func.putty_path(SETTINGS_HOST, SETTINGS_USER, PATH_PUTTY)
            else:
                self.label_9.setText("Putty not found!")
        else:
            os.system("xterm -hold -e 'ssh %s@%s'" % (SETTINGS_USER, SETTINGS_HOST))

    @pyqtSlot(name='on_path_putty')
    def on_path_putty(self):
        self.set_putty()

    @pyqtSlot(name='set_putty')
    def set_putty(self):
        global PATH_PUTTY
        conf_file = QFileDialog.getOpenFileName()
        if conf_file[0] == "":
            return

        PATH_PUTTY = conf_file[0]
        self.lineEdit_10.setText(PATH_PUTTY)

    @pyqtSlot(name='on_path_psplash')
    def on_path_psplash(self):
        self.set_psplash()

    @pyqtSlot(name='set_psplash')
    def set_psplash(self):
        global PATH_PSPLASH
        psplash_file = QFileDialog.getOpenFileName()
        if psplash_file[0] == "":
            return
        PATH_PSPLASH = psplash_file[0]
        self.lineEdit_11.setText(PATH_PSPLASH)

    @pyqtSlot(name='on_path_winscp')
    def on_path_winscp(self):
        self.set_winscp()

    @pyqtSlot(name='set_winscp')
    def set_winscp(self):
        global PATH_WINSCP
        conf_file = QFileDialog.getOpenFileName()
        if conf_file[0] == "":
            return

        PATH_WINSCP = conf_file[0]
        self.lineEdit_9.setText(PATH_WINSCP)

    @pyqtSlot(name='on_button_reboot')
    def on_button_reboot(self):
        func.scp_reboot(SETTINGS_USER, SETTINGS_SECRET, SETTINGS_HOST)
        self.label_9.setText("Reboot command send.")

    @pyqtSlot(name='on_button_poweroff')
    def on_button_poweroff(self):
        func.scp_poweroff(SETTINGS_USER, SETTINGS_SECRET, SETTINGS_HOST)
        self.label_9.setText("Power off command activate.")

    @pyqtSlot(name='on_button_ts_test')
    def on_button_ts_test(self):
        func.scp_ts_test(SETTINGS_USER, SETTINGS_SECRET, SETTINGS_HOST)
        self.label_9.setText('Device stopped. TSLIB_TSDEVICE ts_test launched.')

    @pyqtSlot(name='on_button_ts_calibrate')
    def on_button_ts_calibrate(self):
        func.scp_ts_calibrate(SETTINGS_USER, SETTINGS_SECRET, SETTINGS_HOST)
        self.label_9.setText("Device stopped. TSLIB_TSDEVICE ts_calibrate launched.")

    @pyqtSlot(name='on_button_killall')
    def on_button_killall(self):
        func.scp_killall(SETTINGS_USER, SETTINGS_SECRET, SETTINGS_HOST, SETTINGS_PROJECT)

    @pyqtSlot(name='on_winscp_use')
    def on_winscp_user(self):
        global SETTINGS_UPDATE
        if self.checkBox_3.isChecked():
            self.radioButton.setEnabled(True)
            self.radioButton_2.setEnabled(True)

        elif not self.checkBox.isChecked():
            self.radioButton.setEnabled(False)
            self.radioButton_2.setEnabled(False)
            SETTINGS_UPDATE = '0'
            self.radioButton.setChecked(True)

    @pyqtSlot(name='on_button_open')
    def on_button_open(self):
        global SETTINGS_FILE
        conf_file = QFileDialog.getOpenFileName()
        if conf_file[0] == "":
            return

        SETTINGS_FILE = conf_file[0]
        settings_save()
        settings_load()
        self.settings_init()

    @pyqtSlot(name='on_button_apply')
    def on_button_apply(self):
        global SETTINGS_USER
        global SETTINGS_HOST
        global SETTINGS_SECRET
        global SETTINGS_PROJECT
        global SETTINGS_SOURCE
        global SETTINGS_GLOB_BLD_SRV
        global SETTINGS_GLOB_BS_USR
        global SETTINGS_GLOB_BS_SCRT
        global SETTINGS_UPDATE
        global SETTINGS_FTP_MODE
        global PATH_WINSCP
        global PATH_PUTTY
        global PATH_PSPLASH
        SETTINGS_USER = self.lineEdit_3.text()
        SETTINGS_HOST = self.lineEdit_2.text()
        SETTINGS_SECRET = self.lineEdit_4.text()
        SETTINGS_PROJECT = self.lineEdit.text()
        SETTINGS_SOURCE = self.lineEdit_5.text()
        SETTINGS_GLOB_BLD_SRV = self.lineEdit_6.text()
        SETTINGS_GLOB_BS_USR = self.lineEdit_7.text()
        SETTINGS_GLOB_BS_SCRT = self.lineEdit_8.text()
        if self.radioButton_2.isChecked():
            SETTINGS_UPDATE = '1'
        elif self.radioButton.isChecked():
            SETTINGS_UPDATE = '0'
        if self.checkBox_3.isChecked():
            SETTINGS_FTP_MODE = '1'
        else:
            SETTINGS_FTP_MODE = '0'
        PATH_WINSCP = self.lineEdit_9.text()
        PATH_PUTTY = self.lineEdit_10.text()
        PATH_PSPLASH = self.lineEdit_11.text()
        self.label_9.setText("New configuration applied.")

        # cache saving source history
        fs.cache_save(SETTINGS_SOURCE_HISTORY, SETTINGS_SOURCE)
        # cache saving project name history
        fs.cache_save(SETTINGS_PROJECT_HISTORY, SETTINGS_PROJECT)
        # cache saving device ip history
        fs.cache_save(SETTINGS_DEVICE_IP_HISTORY, SETTINGS_HOST)
        # cache saving winscp path history
        fs.cache_save(SETTINGS_WINSCP_HISTORY, PATH_WINSCP)
        # cache saving putty path history
        fs.cache_save(SETTINGS_PUTTY_HISTORY, PATH_PUTTY)
        # cache saving psplash path history
        fs.cache_save(SETTINGS_PSPLASH_HISTORY, PATH_PSPLASH)

    @pyqtSlot(name='on_path_project')
    def on_path_project(self):
        self.open_file_dialog()

    def open_file_dialog(self):
        global SETTINGS_PROJECT
        path_project = QFileDialog.getExistingDirectory()
        if path_project == "":
            return
        path_tmp = ""
        if os.name == "nt":
            path_tmp = fs.path_double_win(path_project)
        else:
            path_tmp = fs.path_double_nix(path_project)

        print('Path changes with SYSTEM requires: \n')
        print('From: %s\nTo: %s\n' % (path_project, path_tmp))
        SETTINGS_PROJECT = path_tmp
        self.lineEdit_5.setText(SETTINGS_PROJECT)

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
        self.lineEdit_11.clear(0)
        settings_load()
        self.settings_init()
        self.label_9.setText("Configuration re-init")

    @pyqtSlot(name='on_button_save')
    def on_button_save(self):
        global SETTINGS_USER
        global SETTINGS_HOST
        global SETTINGS_SECRET
        global SETTINGS_PROJECT
        global SETTINGS_SOURCE
        global SETTINGS_GLOB_BLD_SRV
        global SETTINGS_GLOB_BS_USR
        global SETTINGS_GLOB_BS_SCRT
        global SETTINGS_UPDATE
        global SETTINGS_FTP_MODE
        global PATH_WINSCP
        global PATH_PUTTY
        global PATH_PSPLASH
        SETTINGS_USER = self.lineEdit_3.text()
        SETTINGS_HOST = self.lineEdit_2.text()
        SETTINGS_SECRET = self.lineEdit_4.text()
        SETTINGS_PROJECT = self.lineEdit.text()
        SETTINGS_SOURCE = self.lineEdit_5.text()
        SETTINGS_GLOB_BLD_SRV = self.lineEdit_6.text()
        SETTINGS_GLOB_BS_USR = self.lineEdit_7.text()
        SETTINGS_GLOB_BS_SCRT = self.lineEdit_8.text()
        if self.radioButton_2.isChecked():
            SETTINGS_UPDATE = '1'
        elif self.radioButton.isChecked():
            SETTINGS_UPDATE = '0'

        if self.checkBox_3.isChecked():
            SETTINGS_FTP_MODE = '1'
        else:
            SETTINGS_FTP_MODE = '0'
        PATH_WINSCP = self.lineEdit_9.text()
        PATH_PUTTY = self.lineEdit_10.text()
        PATH_PSPLASH = self.lineEdit_11.text()
        settings_save()
        self.label_9.setText("Configuration save")

    @pyqtSlot(name='on_button_ping')
    def on_button_ping(self):
        status = func.is_online(SETTINGS_HOST)

        if status == 1:
            self.label_9.setText("Device online [%s status: %d]" % (SETTINGS_HOST, status))
        elif status == 0:
            self.label_9.setText("Device offline [%s status: %d]" % (SETTINGS_HOST, status))

    @pyqtSlot(name='on_button_stop')
    def on_button_stop(self):
        func.scp_stop(SETTINGS_USER, SETTINGS_SECRET, SETTINGS_HOST)
        self.label_9.setText("Stop command has been sent")

    @pyqtSlot(name='on_button_restart')
    def on_button_restart(self):
        func.scp_restart(SETTINGS_USER, SETTINGS_SECRET, SETTINGS_HOST)
        self.label_9.setText("Restart command has been sent")

    def on_working_change(self, value):
        if value == 1:
            self.label_9.setText("Working...")
        elif value == 0:
            self.label_9.setText("Firmware is compiled.")
        else:
            self.label_9.setText("Unknown operation.")

    def on_working_change_debug(self, value):
        if value == 1:
            self.label_9.setText("Working...")
        elif value == 0:
            self.label_9.setText("Firmware is compiled.")
        else:
            self.label_9.setText("Unknown operation.")

    @pyqtSlot(name='on_button_compile_debug')
    def on_button_compile_debug(self):
        self.calc = EProgBar_debug()
        self.calc.working_status_debug.connect(self.on_working_change_debug)
        self.calc.start()

    @pyqtSlot(name='on_button_compile')
    def on_button_compile(self):
        self.calc = EProgBar()
        self.calc.working_status.connect(self.on_working_change)
        self.calc.start()

    @pyqtSlot(name='on_button_upload')
    def on_button_upload(self):
        func.scp_upload(SETTINGS_SOURCE, SETTINGS_PROJECT, SETTINGS_USER, SETTINGS_SECRET, SETTINGS_HOST)
        self.label_9.setText("Update without restarting command has been sent")

    @pyqtSlot(name='on_button_auto')
    def on_button_auto(self):
        print(SETTINGS_USER, SETTINGS_SECRET, SETTINGS_HOST)
        if self.checkBox_2.isChecked():
            func.scp_compile(SETTINGS_SOURCE, SETTINGS_GLOB_BS_USR, SETTINGS_GLOB_BS_SCRT, SETTINGS_PROJECT, SETTINGS_UPDATE, 'release')

        if self.checkBox.isChecked():
            is_online = func.is_online(SETTINGS_HOST, 9999)
            self.label_9.setText("Trying to connect...")
            self.label_9.setText("Connect established.")
            if is_online:
                func.scp_stop(SETTINGS_USER, SETTINGS_SECRET, SETTINGS_HOST)
                func.scp_upload(SETTINGS_SOURCE, SETTINGS_PROJECT, SETTINGS_USER, SETTINGS_SECRET, SETTINGS_HOST)
                func.scp_restart(SETTINGS_USER, SETTINGS_SECRET, SETTINGS_HOST)
                self.label_9.setText("Auto compile&stop&upload command has been sent")
            else:
                self.label_9.setText("process has been interrupted")
        else:
            func.scp_stop(SETTINGS_USER, SETTINGS_SECRET, SETTINGS_HOST)
            func.scp_upload(SETTINGS_SOURCE, SETTINGS_PROJECT, SETTINGS_USER, SETTINGS_SECRET, SETTINGS_HOST)
            func.scp_restart(SETTINGS_USER, SETTINGS_SECRET, SETTINGS_HOST)
            self.label_9.setText("Once compile&stop&upload command has been sent")

    def settings_init(self):
        global SETTINGS_UPDATE
        global PATH_PUTTY_OK
        global PATH_WINSCP_OK
        if len(SETTINGS_PROJECT) == 0:
            self.lineEdit.setText(SETTINGS_EMPTY)
        else:
            self.lineEdit.setText(SETTINGS_PROJECT)

        if len(SETTINGS_HOST) == 0:
            self.lineEdit_2.setText(SETTINGS_EMPTY)
        else:
            self.lineEdit_2.setText(SETTINGS_HOST)

        if len(SETTINGS_USER) == 0:
            self.lineEdit_3.setText(SETTINGS_EMPTY)
        else:
            self.lineEdit_3.setText(SETTINGS_USER)

        if len(SETTINGS_SECRET) == 0:
            self.lineEdit_4.setText(SETTINGS_EMPTY)
        else:
            self.lineEdit_4.setText(SETTINGS_SECRET)

        if len(SETTINGS_SOURCE) == 0:
            self.lineEdit_5.setText(SETTINGS_EMPTY)
        else:
            self.lineEdit_5.setText(SETTINGS_SOURCE)

        if len(SETTINGS_GLOB_BLD_SRV) == 0:
            self.lineEdit_6.setText(SETTINGS_EMPTY)
        else:
            self.lineEdit_6.setText(SETTINGS_GLOB_BLD_SRV)

        if len(SETTINGS_GLOB_BS_USR) == 0:
            self.lineEdit_7.setText(SETTINGS_EMPTY)
        else:
            self.lineEdit_7.setText(SETTINGS_GLOB_BS_USR)

        if len(SETTINGS_GLOB_BS_SCRT) == 0:
            self.lineEdit_8.setText(SETTINGS_EMPTY)
        else:
            self.lineEdit_8.setText(SETTINGS_GLOB_BS_SCRT)

        if SETTINGS_FTP_MODE == '1':
            self.checkBox_3.setChecked(True)
            self.radioButton.setEnabled(True)
            self.radioButton_2.setEnabled(True)
        elif SETTINGS_FTP_MODE == '0':
            self.checkBox_3.setChecked(False)
            self.radioButton.setEnabled(False)
            self.radioButton_2.setEnabled(False)
            SETTINGS_UPDATE = '0'

        if SETTINGS_UPDATE == '0':
            self.radioButton.setChecked(True)
        elif SETTINGS_UPDATE == '1':
            self.radioButton_2.setChecked(True)

        if len(PATH_WINSCP) == 0:
            self.lineEdit_9.setText(SETTINGS_EMPTY)
        else:
            if not os.path.isfile(PATH_WINSCP):
                self.lineEdit_9.setStyleSheet("background-color: red")
                PATH_WINSCP_OK = False
            else:
                PATH_WINSCP_OK = True
            self.lineEdit_9.setText(PATH_WINSCP)

        if len(PATH_PUTTY) == 0:
            self.lineEdit_10.setText(SETTINGS_EMPTY)
        else:
            if not os.path.isfile(PATH_PUTTY):
                self.lineEdit_10.setStyleSheet("background-color: red")
                PATH_PUTTY_OK = False
            else:
                PATH_PUTTY_OK = True
            self.lineEdit_10.setText(PATH_PUTTY)

        if len(PATH_PSPLASH) == 0:
            self.lineEdit_11.setText(SETTINGS_EMPTY)
        else:
            self.lineEdit_11.setText(PATH_PSPLASH)

        fs.cache_read(self.comboBox_3, SETTINGS_SOURCE_HISTORY)
        fs.cache_read(self.comboBox, SETTINGS_PROJECT_HISTORY)
        fs.cache_read(self.comboBox_2, SETTINGS_DEVICE_IP_HISTORY)
        fs.cache_read(self.comboBox_5, SETTINGS_PUTTY_HISTORY)
        fs.cache_read(self.comboBox_4, SETTINGS_WINSCP_HISTORY)
        fs.cache_read(self.comboBox_6, SETTINGS_PSPLASH_HISTORY)

        cache_files_size = 0
        for file in cache_files:
            cache_files_size += os.path.getsize(file)
        self.label_13.setText("%s b" % cache_files_size)


def main():
    import sys
    fs.cache_create(cache_files)
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


def settings_save():
    fp = open(SETTINGS_FILE, 'w')
    fp.write("# Auto created settings file. Remember that value is framed by '' \n")
    check = check_value(SETTINGS_USER)
    fp.write("user = '%s' # user login to device (default: root) \n" % check)
    check = check_value(SETTINGS_HOST)
    fp.write("host = '%s' # device IP \n" % check)
    check = check_value(SETTINGS_SECRET)
    fp.write("secret = '%s' # user pass to device (default: empty) \n" % check)
    check = check_value(SETTINGS_PROJECT)
    fp.write("project = '%s' # project name (sn4215, sn3307) \n" % check)
    check = check_value(SETTINGS_SOURCE)
    fp.write("source = '%s' # path to project (must contain: Build, Src) \n" % check)
    check = check_value(SETTINGS_GLOB_BLD_SRV)
    fp.write("global_build_server = '%s' # Build-Server IP  \n" % check)
    check = check_value(SETTINGS_GLOB_BS_USR)
    fp.write("global_bs_user = '%s' # Your login to build-server \n" % check)
    check = check_value(SETTINGS_GLOB_BS_SCRT)
    fp.write("global_bs_secret = '%s' # Pass\n" % check)
    check = check_value(SETTINGS_UPDATE)
    fp.write("update = '%s' #  0 - update, 1 - sync \n" % check)
    check = check_value(SETTINGS_FTP_MODE)
    fp.write("ftp_mode = '%s' # - 1 - use winSCP, 0 - paramiko  \n" % check)
    check = check_value(PATH_WINSCP)
    fp.write("path_scp = '%s' # - path to WinSCP .com file \n" % check)
    check = check_value(PATH_PUTTY)
    fp.write("path_putty = '%s' # - path to Putty exe file \n" % check)
    check = check_value(PATH_PSPLASH)
    fp.write("path_psplash = '%s' # - path to pslpash file\n" % check)
    fp.close()


def settings_load():
    global SETTINGS_USER 
    global SETTINGS_HOST 
    global SETTINGS_SECRET 
    global SETTINGS_PROJECT 
    global SETTINGS_SOURCE 
    global SETTINGS_GLOB_BLD_SRV 
    global SETTINGS_GLOB_BS_USR 
    global SETTINGS_GLOB_BS_SCRT
    global SETTINGS_UPDATE
    global SETTINGS_FTP_MODE
    global PATH_WINSCP
    global PATH_PUTTY
    global PATH_PSPLASH
    with open(SETTINGS_FILE) as fp:
        for line in fp:
            if line.find('user') == 0:
                index = 4
                SETTINGS_USER = get_value(line, index)

            if line.find('host') == 0:
                index = 4
                SETTINGS_HOST = get_value(line, index)

            if line.find('secret') == 0:
                index = 6
                SETTINGS_SECRET = get_value(line, index)

            if line.find('project') == 0:
                index = 7
                SETTINGS_PROJECT = get_value(line, index)

            if line.find('source') == 0:
                index = 6
                SETTINGS_SOURCE = get_value(line, index)

            if line.find('global_build_server') == 0:
                index = 19
                SETTINGS_GLOB_BLD_SRV = get_value(line, index)

            if line.find('global_bs_user') == 0:
                index = 14
                SETTINGS_GLOB_BS_USR = get_value(line, index)

            if line.find('global_bs_secret') == 0:
                index = 16
                SETTINGS_GLOB_BS_SCRT = get_value(line, index)

            if line.find('update') == 0:
                index = 6
                SETTINGS_UPDATE = get_value(line, index)

            if line.find('ftp_mode') == 0:
                index = 8
                SETTINGS_FTP_MODE = get_value(line, index)

            if line.find('path_scp') == 0:
                index = 8
                PATH_WINSCP = get_value(line, index)

            if line.find('path_putty') == 0:
                index = 10
                PATH_PUTTY = get_value(line, index)

            if line.find('path_psplash') == 0:
                index = 12
                PATH_PSPLASH = get_value(line, index)
        fp.close()


if __name__ == '__main__':
    main()
