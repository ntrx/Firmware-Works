#!/usr/bin/env python
# list of functions for scripts
import os
import settings
import core
import paramiko
import subprocess
from scp import SCPClient
from core import Settings

global_build_server = settings.global_build_server
global_bs_user = settings.global_bs_user
global_bs_secret = settings.global_bs_secret
SETTINGS_FTP_MODE = settings.ftp_mode
PATH_WINSCP = settings.path_scp
PATH_PUTTY = settings.path_putty
pb_overall = 0  # progress bar
pb_total = 0
pb_cur = 0


def createSSHClient(server, port, user, secret):
    client = paramiko.SSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=server, port=port, username=user, password=secret)
    return client


class MySCPClient(SCPClient):
    def put_dir(self, source, target):
        for item in os.listdir(source):
            if os.path.isfile(os.path.join(source, item)):
                self.put(os.path.join(source, item), '%s/%s' % (target, item))
            else:
                self.put_dir(os.path.join(source, item), '%s/%s' % (target, item))


def scp_path(file_name, winscp_path):
    """
    :param file_name: script file name, auto-fill value
    :type file_name: str
    :param winscp_path: loc to winscp.com or winscp.exe
    :type winscp_path: str (regular path)
    :return:
    """
    return os.system("\"%s\" /ini=nul /script=%s" % (winscp_path, file_name))


def scp_command(command, winscp_path):
    # return os.system("\"%s\" %s" % (winscp_path, command))
    CREATE_NO_WINDOW = 0x08000000
    return subprocess.Popen("\"%s\" %s" % (winscp_path, command), creationflags=CREATE_NO_WINDOW)


def putty_path(host, user, path_putty):
    """
    :param host: IP
    :type host: str
    :param user: user name
    :type user: str
    :param path_putty:
    :type path_putty: str (regular path)
    :return:
    """
    CREATE_NO_WINDOW = 0x08000000
    return subprocess.Popen("\"%s\" -ssh %s@%s" % (path_putty, user, host), creationflags=CREATE_NO_WINDOW)


def scp_upload(Settings):
    if os.name == 'nt':
        path_loc_win = Settings.project.path_local + "\\Build\\bin\\" + Settings.project.name + ".bin"
        path_dest_win = "//home//" + Settings.device.user + "//" + Settings.project.name + "//bin//" + Settings.project.name + ".bin"
        if Settings.device.ftp_mode == '1':
            file_name = 'upload' + Settings.device.ip
            f = open(file_name, "w+")
            f.write("option confirm off\n")
            if Settings.device.file_protocol == 'sftp':
                f.write("open sftp://%s:%s@%s/ -hostkey=*\n" % (Settings.device.user, Settings.device.password, Settings.device.ip))
            elif Settings.device.file_protocol == 'scp':
                f.write("open scp://%s@%s:%s/ -hostkey=*\n" % (Settings.device.user, Settings.device.ip, Settings.device.password))
            f.write("put %s %s\n" % (path_loc_win, path_dest_win))
            f.write("chmod 777 \"%s\"\n" % path_dest_win)
            f.write("exit\n")
            f.close()
            scp_path(file_name, PATH_WINSCP)
            os.remove(file_name)
        elif Settings.device.ftp_mode == '0':
            transport = paramiko.Transport((Settings.device.ip, 22))
            transport.connect()
            transport.auth_none(username=Settings.device.user)
            sftp = core.MySFTPClient.from_transport(transport)
            sftp.put(path_loc_win, path_dest_win)
            sftp.chmod(path_dest_win, 777)
            sftp.close()
    else:
        pass
        # linux


def scp_killall(Settings):
    if os.name == 'nt':
        if Settings.device.ftp_mode == '1':  # via winSCP
            file_name = 'killall' + Settings.device.ip
            f = open(file_name, "w+")
            f.write("option confirm off\n")
            if Settings.device.file_protocol == 'sftp':
                f.write("open sftp://%s:%s@%s/ -hostkey=*\n" % (Settings.device.user, Settings.device.password, Settings.device.ip))
            elif Settings.device.file_protocol == 'scp':
                f.write("open scp://%s@%s:%s/ -hostkey=*\n" % (Settings.device.user, Settings.device.ip, Settings.device.password))
            f.write("call killall sn4215_respawn.sh %s.bin\n" % Settings.project.name)
            f.write("exit\n")
            f.close()
            scp_path(file_name, PATH_WINSCP)
            os.remove(file_name)
        if Settings.device.ftp_mode == '0':  # via paramiko
            paramiko.util.log_to_file('killall_command.log')
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            client.connect(hostname=Settings.device.ip, port=22, username=Settings.device.user, password=Settings.device.password)
            client.exec_command("killall sn4215_respawn.sh %s.bin" % Settings.project.name)
            client.close()
    else:
        os.system("ssh %s@%s 'killall sn4215_respawn.sh %s.bin | exit'" % (Settings.device.user, Settings.device.ip, Settings.project.name))


def scp_reboot(Settings):
    if os.name == 'nt':
        if Settings.device.ftp_mode == '1':  # via winSCP
            file_name = 'reboot' + Settings.device.ip
            f = open(file_name, "w+")
            f.write("option confirm off\n")
            if Settings.device.file_protocol == 'sftp':
                f.write("open sftp://%s:%s@%s/ -hostkey=*\n" % (Settings.device.user, Settings.device.password, Settings.device.ip))
            elif Settings.device.file_protocol == 'scp':
                f.write("open scp://%s@%s:%s/ -hostkey=*\n" % (Settings.device.user, Settings.device.ip, Settings.device.password))
            f.write("call shutdown -r now\n")  # shutdown -r now - on default linux its works
            f.write("exit\n")
            f.close()
            scp_path(file_name, PATH_WINSCP)
            os.remove(file_name)
        if Settings.device.ftp_mode == '0':  # via paramiko
            paramiko.util.log_to_file('reboot_command.log')
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            client.connect(Settings.device.ip, 22, Settings.device.user, Settings.device.password)
            client.exec_command("sudo reboot")
            client.close()
    else:
        os.system("ssh %s@%s 'sudo reboot | exit'" % (Settings.device.user, Settings.device.ip))


def scp_poweroff(Settings):
    if os.name == 'nt':
        if Settings.device.ftp_mode == '1':  # via winSCP
            file_name = 'poweroff' + Settings.device.ip
            f = open(file_name, "w+")
            f.write("option confirm off\n")
            if Settings.device.file_protocol == 'sftp':
                f.write("open sftp://%s:%s@%s/ -hostkey=*\n" % (Settings.device.user, Settings.device.password, Settings.device.ip))
            elif Settings.device.file_protocol == 'scp':
                f.write("open scp://%s@%s:%s/ -hostkey=*\n" % (Settings.device.user, Settings.device.ip, Settings.device.password))
            f.write("call poweroff\n")
            f.write("exit\n")
            f.close()
            scp_path(file_name, PATH_WINSCP)
            os.remove(file_name)
        if Settings.device.ftp_mode == '0':  # via paramiko
            paramiko.util.log_to_file('poweroff_command.log')
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            client.connect(Settings.device.ip, 22, Settings.device.user, Settings.device.password)
            client.exec_command("poweroff")
            client.close()
    else:
        os.system("ssh %s@%s 'poweroff | exit'" % (Settings.device.user, Settings.device.ip))


def scp_ts_test(Settings):
    if os.name == 'nt':
        if Settings.device.ftp_mode == '1':  # via winSCP
            file_name = 'ts_test' + Settings.device.ip
            f = open(file_name, "w+")
            f.write("option confirm off\n")
            if Settings.device.file_protocol == 'sftp':
                f.write("open sftp://%s:%s@%s/ -hostkey=*\n" % (Settings.device.user, Settings.device.password, Settings.device.ip))
            elif Settings.device.file_protocol == 'scp':
                f.write("open scp://%s@%s:%s/ -hostkey=*\n" % (Settings.device.user, Settings.device.ip, Settings.device.password))
            f.write("call /etc/init.d/autorun.sh stop\n")
            f.write("call TSLIB_TSDEVICE=/dev/input/event2 ts_test\n")
            f.write("exit\n")
            f.close()
            scp_path(file_name, PATH_WINSCP)
            os.remove(file_name)
        if Settings.device.ftp_mode == '0':  # via paramiko
            paramiko.util.log_to_file('ts_test_command.log')
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            client.connect(Settings.device.ip, 22, Settings.device.user, Settings.device.password)
            client.exec_command("/etc/init.d/autorun.sh stop")
            client.exec_command("TSLIB_TSDEVICE=/dev/input/event2 ts_test")
            client.close()
    else:
        os.system("ssh %s@%s '/etc/init.d/autorun.sh stop | TSLIB_TSDEVICE=/dev/input/event2 ts_test | exit'" % (Settings.device.user, Settings.device.ip))


def scp_ts_calibrate(Settings):
    if os.name == 'nt':
        if Settings.device.ftp_mode == '1':  # via winSCP
            file_name = 'ts_calibrate' + Settings.device.ip
            f = open(file_name, "w+")
            f.write("option confirm off\n")
            if Settings.device.file_protocol == 'sftp':
                f.write("open sftp://%s:%s@%s/ -hostkey=*\n" % (Settings.device.user, Settings.device.password, Settings.device.ip))
            elif Settings.device.file_protocol == 'scp':
                f.write("open scp://%s@%s:%s/ -hostkey=*\n" % (Settings.device.user, Settings.device.ip, Settings.device.password))
            f.write("call /etc/init.d/autorun.sh stop\n")
            f.write("call TSLIB_TSDEVICE=/dev/input/event2 ts_calibrate\n")
            f.write("exit\n")
            f.close()
            scp_path(file_name, Settings.local.path_winscp)
            os.remove(file_name)
        if Settings.device.ftp_mode == '0':  # via paramiko
            paramiko.util.log_to_file('ts_calibrate_command.log')
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            client.connect(Settings.device.ip, 22, Settings.device.user, Settings.device.password)
            client.exec_command("/etc/init.d/autorun.sh stop")
            client.exec_command("TSLIB_TSDEVICE=/dev/input/event2 ts_calibrate")
            client.close()
    else:
        os.system("ssh %s@%s '/etc/init.d/autorun.sh stop | TSLIB_TSDEVICE=/dev/input/event2 ts_calibrate | exit'" % (Settings.device.user, Settings.device.ip))


def scp_stop(Settings):
    if os.name == 'nt':
        if Settings.device.ftp_mode == '1':  # via winSCP
            file_name = 'stop' + Settings.device.ip
            f = open(file_name, "w+")
            f.write("option confirm off\n")
            if Settings.device.file_protocol == 'sftp':
                f.write("open sftp://%s:%s@%s/ -hostkey=*\n" % (Settings.device.user, Settings.device.password, Settings.device.ip))
            elif Settings.device.file_protocol == 'scp':
                f.write("open scp://%s@%s:%s/ -hostkey=*\n" % (Settings.device.user, Settings.device.ip, Settings.device.password))
            f.write("call /etc/init.d/autorun.sh stop\n")
            f.write("exit\n")
            f.close()
            scp_path(file_name, Settings.local.path_winscp)
            os.remove(file_name)
        if Settings.device.ftp_mode == '0':  # via paramiko
            paramiko.util.log_to_file('stop_command.log')
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            client.connect(Settings.device.ip, 22, Settings.device.user, Settings.device.password)
            client.exec_command("/etc/init.d/autorun.sh stop")
            client.close()
    else:
        os.system("ssh %s@%s '/etc/init.d/autorun.sh stop | exit'" % (Settings.device.user, Settings.device.ip))


def scp_restart(Settings):
    if os.name == 'nt':
        file_name = 'restart' + Settings.device.ip
        if Settings.device.ftp_mode == '1':  # via winSCP
            f = open(file_name, "w+")
            f.write("option confirm off\n")
            if Settings.device.file_protocol == 'sftp':
                f.write("open sftp://%s:%s@%s/ -hostkey=*\n" % (Settings.device.user, Settings.device.password, Settings.device.ip))
            elif Settings.device.file_protocol == 'scp':
                f.write("open scp://%s@%s:%s/ -hostkey=*\n" % (Settings.device.user, Settings.device.ip, Settings.device.password))
            f.write("call /etc/init.d/autorun.sh restart\n")
            f.write("exit\n")
            f.close()
            scp_path(file_name, Settings.local.path_winscp)
            os.remove(file_name)
        if Settings.device.ftp_mode == '0':  # via paramiko
            paramiko.util.log_to_file('restart_command.log')
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            if Settings.device.password == '':
                print('using no password')
                client.connect(hostname=Settings.device.ip, port=22, username=Settings.device.user)
            else:
                print('using passwprd')
                client.connect(Settings.device.ip, 22, Settings.device.user, Settings.device.password)
            print('do')
            client.exec_command("/etc/init.d/autorun.sh restart")
            client.close()
    else:
        os.system("ssh %s@%s '/etc/init.d/autorun.sh restart | exit'" % (Settings.device.user, Settings.device.ip))


# return 1 if online
def is_online(host, times=1):
    if os.name == 'nt':
        ping_status = subprocess.call("ping -n %d %s" % (times, host))
        if ping_status == 0:  # active
            return 1
        elif ping_status == 0:
            return 0
        elif ping_status > 0:
            return 0
        elif ping_status < 0:
            return 0
        else:
            return 0

    else:
        ping_status = os.system("ping -c %d %s" % (times, host))
        if ping_status == 0:
            return 1
        else:
            return 0


def scp_compile(Settings, build):
    if os.name == 'nt':
        path_loc_win = Settings.project.path_local  # os.getcwd()
        path_dest_win = "//home//" + Settings.server.user + Settings.server.path_external
        file_name = 'compile' + Settings.project.name
        if not os.path.isdir(path_loc_win + "\\Build\\bin\\"):
            os.mkdir(path_loc_win + "\\Build\\bin\\")
        if Settings.device.ftp_mode == '1':
            f = open(file_name, 'w+')
            f.write("option confirm off\n")
            f.write("open sftp://%s:%s@%s/ -hostkey=*\n" % (Settings.server.user, Settings.server.password, Settings.server.ip))
            if Settings.server.sync_files == '0':
                f.write("mkdir //home//%s//%s\n" % (Settings.server.user, Settings.server.path_external))
                f.write("put -filemask=*|%s/Src/Windows/device/ %s %s//Src\n" % (path_loc_win, path_loc_win + "\\Src", path_dest_win))
            elif Settings.server.sync_files == '1':
                f.write("synchronize -filemask=*|%s/Src/Windows/device/ remote %s %s//Src\n" % (path_loc_win, path_loc_win + "\\Src", path_dest_win))
            f.write("cd //home//" + Settings.server.user + Settings.server.path_external + "//Src\n")
            if not Settings.server.compile_mode:
                f.write("call make clean\n")
            if build == 'release':
                f.write("call make %s -j7\n" % Settings.server.compiler)
            elif build == 'debug':
                f.write("call make %s debug -j7\n" % Settings.server.compiler)
            else:
                print("Error while exclude code, exiting.")
                return
            f.write("cd ..\n")
            f.write("cd Build//bin//\n")
            f.write("get %s %s\n" % (Settings.project.name + ".bin", path_loc_win + "\\Build\\bin\\" + Settings.project.name + ".bin\n"))
            f.write("exit\n")
            f.close()

            result = scp_path(file_name, Settings.local.path_winscp)
            # replace /script with /command
            os.remove(file_name)

            if result >= 1:
                print("error while executing code")
                print(result)

        if Settings.device.ftp_mode == '0':
            transport = paramiko.Transport(global_build_server, 22)
            transport.connect(username=Settings.server.user, password=Settings.server.password)
            sftp = core.MySFTPClient.from_transport(transport)
            if Settings.server.sync_files == '0':
                sftp.mkdir(path_dest_win, ignore_existing=True)
                sftp.put_dir(path_loc_win, path_dest_win)
            elif Settings.server.sync_files == '1':
                pass

            paramiko.util.log_to_file('compile.log')
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            client.connect(global_build_server, 22, Settings.server.user, Settings.server.password)
            if Settings.server.sync_files == '0':
                print("Join ", Settings.server.path_external + "/Src")
                stdin, stdout, stderr = client.exec_command("cd " + Settings.server.path_external + "/Src;")
                print("make begin")
                stdin, stdout, stderr = client.exec_command("make clean; make %s" % Settings.server.compiler)
                print("make end")
            # data = stdout.read() + stderr.read()
            elif Settings.server.sync_files == '1':
                stdin, stdout, stderr = client.exec_command("cd " + Settings.server.path_external + "/Src; make %s" % Settings.server.compiler)
            # data = stdout.read() + stderr.read()
            client.close()
            print("Getting file: " + Settings.server.path_external + "/Build/bin/" + Settings.project.name + ".bin")
            sftp.get(remotepath="/home/" + Settings.server.user + "/" + Settings.server.path_external + "/Build/bin/" + Settings.project.name + ".bin",
                     localpath=path_loc_win + "\\Build\\bin\\" + Settings.project.name + ".bin")
            print("Saving to: " + path_loc_win + "\\Build\\bin\\" + Settings.project.name + ".bin")
            sftp.close()
    else:
        pass  # in process


def scp_detect_project(Settings, self):
    if Settings.device.file_protocol == 'sftp':
        transport = paramiko.Transport((Settings.device.ip, 22))
        transport.connect()
        transport.auth_none(username=Settings.device.user)
        sftp = core.MySFTPClient.from_transport(transport)
        result = sftp.listdir("/home/root/")
        for obj in result:
            if obj[0] != '.':
                result = obj
                break
            else:
                result = 'None'
        sftp.close()
        self.setText("Detected firmware: %s" % result)
    elif Settings.device.file_protocol == 'scp':
        if os.name == "nt":
            self.setText('Cannot get directory list via SCP.')
        else:
            pass


def scp_detect_outdated_firmware(Settings, self):
    local_firmware = os.stat('%s/Build/bin/%s.bin' % (Settings.project.path_local, Settings.project.name))
    if Settings.device.file_protocol == 'sftp':
        transport = paramiko.Transport((Settings.device.ip, 22))
        transport.connect()
        transport.auth_none(username=Settings.device.user)
        sftp = core.MySFTPClient.from_transport(transport)
        device_firmware = sftp.lstat('/home/root/%s/bin/%s.bin' % (Settings.project.name, Settings.project.name))
        sftp.close()
    elif Settings.device.file_protocol == 'scp':
        transport = paramiko.Transport((Settings.device.ip, 22))
        transport.connect()
        transport.auth_none(username=Settings.device.user)
        scp = SCPClient(transport)
        scp.get('/home/root/%s/bin/%s.bin' % (Settings.project.name, Settings.project.name), '%s/Build/bin/%s-remote' % (Settings.project.path_local, Settings.project.name))
        device_firmware = os.stat('%s/Build/bin/%s-remote' % (Settings.project.path_local, Settings.project.name))

    if device_firmware.st_mtime < float(local_firmware.st_mtime):
        self.setText("Firmware is outdated!")
    elif device_firmware.st_mtime > float(local_firmware.st_mtime):
        self.setText("Firmware is newer than local!")
    elif device_firmware.st_mtime == float(local_firmware.st_mtime):
        self.setText("Firmware is similar to local!")
    else:
        self.setText("Unavailable to compare firmwares!")


def scp_psplash_upload(Settings, self):
    if os.name == 'nt':
        file_name = core.fs.path_get_filename(Settings.project.path_psplash)
        path_loc_win = Settings.project.path_psplash
        path_dest_win = "//usr//bin//" + file_name
        if Settings.device.ftp_mode == '1':
            file_name = 'psplash' + Settings.device.ip
            f = open(file_name, "w+")
            f.write("option confirm off\n")
            if Settings.device.file_protocol == 'sftp':
                f.write("open sftp://%s:%s@%s/ -hostkey=*\n" % (Settings.device.user, Settings.device.password, Settings.device.ip))
            elif Settings.device.file_protocol == 'scp':
                f.write("open scp://%s@%s:%s/ -hostkey=*\n" % (Settings.device.user, Settings.device.ip, Settings.device.password))
            f.write("put %s %s\n" % (path_loc_win, path_dest_win))
            f.write("chmod 777 %s\n" % path_dest_win)
            f.write("call ln -sfn %s psplash\n" % path_dest_win)
            f.write("exit\n")
            f.close()
            scp_path(file_name, PATH_WINSCP)
            os.remove(file_name)
        elif Settings.device.ftp_mode == '0':
            transport = paramiko.Transport((Settings.device.ip, 22))
            transport.connect()
            transport.auth_none(username=Settings.device.user)
            sftp = core.MySFTPClient.from_transport(transport)
            sftp.put(path_loc_win, path_dest_win)
            sftp.chmod(path_dest_win, 777)
            sftp.close()
        self.setText("psplash command sent")
    else:
        pass
        # linux


def scp_clean(Settings):
    if os.name == 'nt':
        # path_dest_win = "//home//" + Settings.server.user + Settings.server.path_external
        file_name = 'clean' + Settings.server.ip
        if Settings.device.ftp_mode == '1':
            f = open(file_name, 'w+')
            f.write("option confirm off\n")
            if Settings.device.file_protocol == 'sftp':
                f.write("open sftp://%s:%s@%s/ -hostkey=*\n" % (Settings.server.user, Settings.server.password, Settings.server.ip))
            elif Settings.device.file_protocol == 'scp':
                f.write("open scp://%s@%s:%s/ -hostkey=*\n" % (Settings.server.user, Settings.server.ip, Settings.server.password))
            f.write("cd //home//" + global_bs_user + Settings.server.path_external + "//Src\n")
            f.write("call make clean\n")
            f.write("exit\n")
            f.close()

            result = scp_path(file_name, Settings.local.path_winscp)
            # replace /script with /command
            os.remove(file_name)

            if result >= 1:
                print("error while executing code")
                print(result)

        if Settings.device.ftp_mode == '0':
            transport = paramiko.Transport(global_build_server, 22)
            transport.connect(username=Settings.server.user, password=Settings.server.password)
            sftp = core.MySFTPClient.from_transport(transport)

            paramiko.util.log_to_file('clean.log')
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            client.connect(Settings.server.ip, 22, Settings.server.user, Settings.server.password)
            stdin, stdout, stderr = client.exec_command("cd " + Settings.server.path_external + "/Src;")
            stdin, stdout, stderr = client.exec_command("make clean")
            # data = stdout.read() + stderr.read()
            client.close()
            sftp.close()
    else:
        pass  # in process


def sftp_callback(transferred, toBeTransferred):
    print("Transferred: {0}\tOut of: {1}".format(transferred, toBeTransferred))
