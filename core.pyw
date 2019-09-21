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

SETTINGS_EMPTY: str = ""
SETTINGS_FILE: str = "settings.py"
SETTINGS_SOURCE_HISTORY = "source-history.log"
SETTINGS_PROJECT_HISTORY = "project-history.log"
SETTINGS_DEVICE_IP_HISTORY = "device-ip-history.log"
SETTINGS_WINSCP_HISTORY = "winscp-history.log"
SETTINGS_PUTTY_HISTORY = "putty-history.log"


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
        self.toolButton_2.clicked.connect(self.on_path_project)
        self.pushButton_8.clicked.connect(self.on_button_apply)
        self.pushButton_10.clicked.connect(self.on_button_open)
        self.pushButton_11.clicked.connect(self.on_button_killall)
        self.pushButton_14.clicked.connect(self.on_button_ts_test)
        self.pushButton_13.clicked.connect(self.on_button_ts_calibrate)
        self.pushButton_15.clicked.connect(self.on_button_poweroff)
        self.pushButton_16.clicked.connect(self.on_button_reboot)
        self.toolButton_3.clicked.connect(self.on_path_winscp)
        self.toolButton_4.clicked.connect(self.on_path_putty)
        self.pushButton_17.clicked.connect(self.on_open_putty)
        self.pushButton_18.clicked.connect(self.on_button_compile_debug)
        self.pushButton_19.clicked.connect(self.on_button_edit)
        self.pushButton_20.clicked.connect(self.on_button_clear_cache)

        # check boxes
        self.checkBox_3.clicked.connect(self.on_winscp_use)

        # comboboxes
        self.comboBox.currentIndexChanged.connect(self.on_project_change)
        self.comboBox_3.currentIndexChanged.connect(self.on_source_change)
        self.comboBox_2.currentIndexChanged.connect(self.on_device_ip_change)
        self.comboBox_4.currentIndexChanged.connect(self.on_winscp_change)
        self.comboBox_5.currentIndexChanged.connect(self.on_putty_change)

    @pyqtSlot(name='on_button_clear_cache')
    def on_button_clear_cache(self):
        cache_files = [SETTINGS_DEVICE_IP_HISTORY, SETTINGS_PROJECT_HISTORY, SETTINGS_PUTTY_HISTORY, SETTINGS_WINSCP_HISTORY, SETTINGS_SOURCE_HISTORY]

        for file in cache_files:
            f = open(file, "w")
            f.write("")
            f.close()

        self.on_button_apply()
        self.label_9.setText("Cached information has been clear.")

    @pyqtSlot(name='on_button_edit')
    def on_button_edit(self):
        CREATE_NO_WINDOW = 0x08000000
        return subprocess.Popen("notepad %s" % SETTINGS_FILE, creationflags=CREATE_NO_WINDOW)

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
        func.putty_path(SETTINGS_HOST, SETTINGS_USER, PATH_PUTTY)

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
        settings_save()
        settings_load()
        self.settings_init()

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
        settings_save()
        settings_load()
        self.settings_init()

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

    @pyqtSlot(name='on_path_project')
    def on_path_project(self):
        self.open_file_dialog()

    def open_file_dialog(self):
        global SETTINGS_PROJECT
        path_project = QFileDialog.getExistingDirectory()
        if path_project == "":
            return
        path_tmp = ""
        for letter in range(0, len(path_project)):
            if path_project[letter] == '/':
                path_tmp += "\\"
                continue
            path_tmp += path_project[letter]

        print(path_tmp)
        SETTINGS_PROJECT = path_tmp
        self.lineEdit_5.setText(SETTINGS_PROJECT)

    @pyqtSlot(name='on_button_reload')
    def on_button_reload(self):
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
            is_online = func.is_online(SETTINGS_HOST)
            self.label_9.setText("Trying to connect...")
            while is_online == 0:
                is_online = func.is_online(SETTINGS_HOST)
                self.label_9.setText("Trying to connect...")
            self.label_9.setText("Connect established.")
        
        func.scp_stop(SETTINGS_USER, SETTINGS_SECRET, SETTINGS_HOST)
        func.scp_upload(SETTINGS_SOURCE, SETTINGS_PROJECT, SETTINGS_USER, SETTINGS_SECRET, SETTINGS_HOST)
        func.scp_restart(SETTINGS_USER, SETTINGS_SECRET, SETTINGS_HOST)
        self.label_9.setText("Auto compile&stop&upload command has been sent")

    def settings_init(self):
        global SETTINGS_UPDATE
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
            self.lineEdit_9.setText(PATH_WINSCP)

        if len(PATH_PUTTY) == 0:
            self.lineEdit_10.setText(SETTINGS_EMPTY)
        else:
            if not os.path.isfile(PATH_PUTTY):
                self.lineEdit_10.setStyleSheet("background-color: red")
            self.lineEdit_10.setText(PATH_PUTTY)

        fs.cache_read(self.comboBox_3, SETTINGS_SOURCE_HISTORY)
        fs.cache_read(self.comboBox, SETTINGS_PROJECT_HISTORY)
        fs.cache_read(self.comboBox_2, SETTINGS_DEVICE_IP_HISTORY)
        fs.cache_read(self.comboBox_4, SETTINGS_PUTTY_HISTORY)
        fs.cache_read(self.comboBox_5, SETTINGS_WINSCP_HISTORY)


def main():
    import sys
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


def settings_save():
    fp = open(SETTINGS_FILE, 'w')
    fp.write("# Auto created settings file. Remember that value is framed by '' \n")
    fp.write("user = '%s' # user login to device (root) \n" % SETTINGS_USER)
    fp.write("host = '%s' # device IP \n" % SETTINGS_HOST)
    fp.write("secret = '%s' # user pass to device (empty) \n" % SETTINGS_SECRET)
    fp.write("project = '%s' # project name (sn4215, sn3307) \n" % SETTINGS_PROJECT)
    fp.write("source = '%s' # path to project (must contain: Build, Src) \n" % SETTINGS_SOURCE)
    fp.write("global_build_server = '%s' # Build-Server IP  \n" % SETTINGS_GLOB_BLD_SRV)
    fp.write("global_bs_user = '%s' # Your login to build-server \n" % SETTINGS_GLOB_BS_USR)
    fp.write("global_bs_secret = '%s' # Pass\n" % SETTINGS_GLOB_BS_SCRT)
    fp.write("update = '%s' #  0 - update, 1 - sync \n" % SETTINGS_UPDATE)
    fp.write("ftp_mode = '%s' # - 1 - use winSCP, 0 - paramiko  \n" % SETTINGS_FTP_MODE)
    fp.write("path_scp = '%s' # - path to WinSCP .com file \n" % PATH_WINSCP)
    fp.write("path_putty = '%s' # - path to Putty exe file \n" % PATH_PUTTY)


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
            else:
                SETTINGS_FTP_MODE = '1'

            if line.find('path_scp') == 0:
                index = 8
                PATH_WINSCP = get_value(line, index)

            if line.find('path_putty') == 0:
                index = 10
                PATH_PUTTY = get_value(line, index)


if __name__ == '__main__':
    main()
