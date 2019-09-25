#!/usr/bin/env python
# list of functions for scripts
import os
import settings
import core
import paramiko
import subprocess

global_build_server = settings.global_build_server
global_bs_user = settings.global_bs_user
global_bs_secret = settings.global_bs_secret
SETTINGS_FTP_MODE = settings.ftp_mode
PATH_WINSCP = settings.path_scp
PATH_PUTTY = settings.path_putty
pb_overall = 0  # progress bar
pb_total = 0
pb_cur = 0


def scp_path(file_name, winscp_path=PATH_WINSCP):
    """
    :param file_name: script file name, auto-fill value
    :type file_name: str
    :param winscp_path: loc to winscp.com or winscp.exe
    :type winscp_path: str (regular path)
    :return:
    """
    return os.system("\"%s\" /ini=nul /script=%s" % (winscp_path, file_name))


def putty_path(host, user, path_putty=PATH_PUTTY):
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


def scp_upload(source, project, user, secret, host):
    if os.name == 'nt':
        path_loc_win = source + "\\Build\\bin\\" + project + ".bin"
        path_dest_win = "//home//" + user + "//" + project + "//bin//" + project + ".bin"
        if SETTINGS_FTP_MODE == '1':
            file_name = 'upload' + host
            f = open(file_name, "w+")
            f.write("option confirm off\n")
            f.write("open sftp://%s:%s@%s/ -hostkey=*\n" % (user, secret, host))
            f.write("put %s %s\n" % (path_loc_win, path_dest_win))
            f.write("exit\n")
            f.close()
            scp_path(file_name, PATH_WINSCP)
            os.remove(file_name)
        elif SETTINGS_FTP_MODE == '0':
            transport = paramiko.Transport((host, 22))
            transport.connect()
            transport.auth_none(username=user)
            sftp = core.MySFTPClient.from_transport(transport)
            sftp.put(path_loc_win, path_dest_win)
            sftp.close()
    else:
        pass
        # linux


def scp_killall(user, secret, host, project):
    if os.name == 'nt':
        if SETTINGS_FTP_MODE == '1':  # via winSCP
            file_name = 'killall' + host
            f = open(file_name, "w+")
            f.write("option confirm off\n")
            f.write("open sftp://%s:%s@%s/ -hostkey=*\n" % (user, secret, host))
            f.write("call killall sn4215_respawn.sh %s.bin\n" % project)
            f.write("exit\n")
            f.close()
            scp_path(file_name, PATH_WINSCP)
            os.remove(file_name)
        if SETTINGS_FTP_MODE == '0':  # via paramiko
            paramiko.util.log_to_file('killall_command.log')
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            client.connect(hostname=host, port=22, username=user, password=secret)
            client.exec_command("killall sn4215_respawn.sh %s.bin" % project)
            client.close()
    else:
        os.system("ssh %s@%s 'killall sn4215_respawn.sh %s.bin | exit'" % (user, host, project))
    #linux


def scp_reboot(user, secret, host):
    if os.name == 'nt':
        if SETTINGS_FTP_MODE == '1':  # via winSCP
            file_name = 'reboot' + host
            f = open(file_name, "w+")
            f.write("option confirm off\n")
            f.write("open sftp://%s:%s@%s/ -hostkey=*\n" % (user, secret, host))
            f.write("call shutdown -r now\n")
            f.write("exit\n")
            f.close()
            scp_path(file_name, PATH_WINSCP)
            os.remove(file_name)
        if SETTINGS_FTP_MODE == '0':  # via paramiko
            paramiko.util.log_to_file('reboot_command.log')
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            client.connect(host, 22, user, secret)
            client.exec_command("shutdown -r now")
            client.close()
    else:
        os.system("ssh %s@%s 'shutdown -r now | exit'" % (user, host))


def scp_poweroff(user, secret, host):
    if os.name == 'nt':
        if SETTINGS_FTP_MODE == '1':  # via winSCP
            file_name = 'poweroff' + host
            f = open(file_name, "w+")
            f.write("option confirm off\n")
            f.write("open sftp://%s:%s@%s/ -hostkey=*\n" % (user, secret, host))
            f.write("call poweroff\n")
            f.write("exit\n")
            f.close()
            scp_path(file_name, PATH_WINSCP)
            os.remove(file_name)
        if SETTINGS_FTP_MODE == '0':  # via paramiko
            paramiko.util.log_to_file('poweroff_command.log')
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            client.connect(host, 22, user, secret)
            client.exec_command("poweroff")
            client.close()
    else:
        os.system("ssh %s@%s 'poweroff | exit'" % (user, host))


def scp_ts_test(user, secret, host):
    if os.name == 'nt':
        if SETTINGS_FTP_MODE == '1':  # via winSCP
            file_name = 'ts_test' + host
            f = open(file_name, "w+")
            f.write("option confirm off\n")
            f.write("open sftp://%s:%s@%s/ -hostkey=*\n" % (user, secret, host))
            f.write("call /etc/init.d/autorun.sh stop\n")
            f.write("call TSLIB_TSDEVICE=/dev/input/event2 ts_test\n")
            f.write("exit\n")
            f.close()
            scp_path(file_name, PATH_WINSCP)
            os.remove(file_name)
        if SETTINGS_FTP_MODE == '0':  # via paramiko
            paramiko.util.log_to_file('ts_test_command.log')
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            client.connect(host, 22, user, secret)
            client.exec_command("/etc/init.d/autorun.sh stop")
            client.exec_command("TSLIB_TSDEVICE=/dev/input/event2 ts_test")
            client.close()
    else:
        os.system("ssh %s@%s '/etc/init.d/autorun.sh stop | TSLIB_TSDEVICE=/dev/input/event2 ts_test | exit'" % (user, host))


def scp_ts_calibrate(user, secret, host):
    if os.name == 'nt':
        if SETTINGS_FTP_MODE == '1':  # via winSCP
            file_name = 'ts_calibrate' + host
            f = open(file_name, "w+")
            f.write("option confirm off\n")
            f.write("open sftp://%s:%s@%s/ -hostkey=*\n" % (user, secret, host))
            f.write("call /etc/init.d/autorun.sh stop\n")
            f.write("call TSLIB_TSDEVICE=/dev/input/event2 ts_calibrate\n")
            f.write("exit\n")
            f.close()
            scp_path(file_name)
            os.remove(file_name)
        if SETTINGS_FTP_MODE == '0':  # via paramiko
            paramiko.util.log_to_file('ts_calibrate_command.log')
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            client.connect(host, 22, user, secret)
            client.exec_command("/etc/init.d/autorun.sh stop")
            client.exec_command("TSLIB_TSDEVICE=/dev/input/event2 ts_calibrate")
            client.close()
    else:
        os.system("ssh %s@%s '/etc/init.d/autorun.sh stop | TSLIB_TSDEVICE=/dev/input/event2 ts_calibrate | exit'" % (user, host))


def scp_stop(user, secret, host):
    if os.name == 'nt':
        if SETTINGS_FTP_MODE == '1':  # via winSCP
            file_name = 'stop' + host
            f = open(file_name, "w+")
            f.write("option confirm off\n")
            f.write("open sftp://%s:%s@%s/ -hostkey=*\n" % (user, secret, host))
            f.write("call /etc/init.d/autorun.sh stop\n")
            f.write("exit\n")
            f.close()
            scp_path(file_name)
            os.remove(file_name)
        if SETTINGS_FTP_MODE == '0':  # via paramiko
            paramiko.util.log_to_file('stop_command.log')
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            client.connect(host, 22, user, secret)
            client.exec_command("/etc/init.d/autorun.sh stop")
            client.close()
    else:
        os.system("ssh %s@%s '/etc/init.d/autorun.sh stop | exit'" % (user, host))


def scp_restart(user, secret, host):
    if os.name == 'nt':
        file_name = 'restart' + host
        if SETTINGS_FTP_MODE == '1':  # via winSCP
            f = open(file_name, "w+")
            f.write("option confirm off\n")
            f.write("open sftp://%s:%s@%s/ -hostkey=*\n" % (user, secret, host))
            f.write("call /etc/init.d/autorun.sh restart\n")
            f.write("exit\n")
            f.close()
            scp_path(file_name)
            os.remove(file_name)
        if SETTINGS_FTP_MODE == '0':  # via paramiko
            paramiko.util.log_to_file('restart_command.log')
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            if secret == '':
                print('using no password')
                client.connect(hostname=host, port=22, username=user)
            else:
                print('using passwprd')
                client.connect(host, 22, user, secret)
            print('do')
            client.exec_command("/etc/init.d/autorun.sh restart")
            client.close()
    else:
        os.system("ssh %s@%s '/etc/init.d/autorun.sh restart | exit'" % (user, host))


# return 1 if online
def is_online(host, times=1):
    if os.name == 'nt':
        ping_status = subprocess.call("ping -n %d %s" % (times, host))
        if ping_status == 0:  # active
            return 1
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


# isUpdate = 1 :: files already been on SERVER (SYNC, faster)
# isUpdate = 0 :: no file on server, its first upload
# build (release or debug type)
def scp_compile(source, user, secret, project, is_update, build='release'):
    if os.name == 'nt':
        path_loc_win = source  # os.getcwd()
        path_dest_win = "//home//" + user + "//projects//" + project
        file_name = 'compile' + project
        if SETTINGS_FTP_MODE == '1':
            f = open(file_name, 'w+')
            f.write("option confirm off\n")
            f.write("open sftp://%s:%s@%s/ -hostkey=*\n" % (user, secret, global_build_server))
            if is_update == '0':
                f.write("put %s %s//Src\n" % (path_loc_win + "\\Src", path_dest_win))
            elif is_update == '1':
                f.write("synchronize remote %s %s//Src\n" % (path_loc_win + "\\Src", path_dest_win))
            f.write("cd //home//" + global_bs_user + "//projects//" + project + "//Src\n")
            f.write("call make clean\n")
            if build == 'release':
                f.write("call make -j7\n")
            elif build == 'debug':
                f.write("call make debug -j7\n")
            else:
                print("Error while exclude code, exiting.")
                return
            f.write("cd ..\n")
            f.write("cd Build//bin//\n")
            f.write("get %s %s\n" % (project + ".bin", path_loc_win + "\\Build\\bin\\" + project + ".bin\n"))
            f.write("exit\n")
            f.close()

            result = scp_path(file_name)
            # replace /script with /command
            os.remove(file_name)

            if result >= 1:
                print("error while executing code")
                print(result)

        if SETTINGS_FTP_MODE == '0':
            transport = paramiko.Transport(global_build_server, 22)
            transport.connect(username=user, password=secret)
            sftp = core.MySFTPClient.from_transport(transport)
            if is_update == '0':
                sftp.mkdir(path_dest_win, ignore_existing=True)
                sftp.put_dir(path_loc_win, path_dest_win)
            elif is_update == '1':
                pass

            paramiko.util.log_to_file('compile.log')
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            client.connect(global_build_server, 22, user, secret)
            if is_update == '0':
                stdin, stdout, stderr = client.exec_command("cd projects/" + project + "/Src; make clean; make")
            # data = stdout.read() + stderr.read()
            elif is_update == '1':
                stdin, stdout, stderr = client.exec_command("cd projects/" + project + "/Src; make")
            # data = stdout.read() + stderr.read()
            client.close()
            sftp.get(remotepath="projects/" + project + "/Build/bin/" + project + ".bin",
                     localpath=path_loc_win + "\\Build\\bin\\" + project + ".bin")
            sftp.close()
    else:
        pass  # in process


def scp_detect_project(host, user, secret):
    transport = paramiko.Transport((host, 22))
    transport.connect()
    transport.auth_none(username=user)
    sftp = core.MySFTPClient.from_transport(transport)
    result = sftp.listdir("/home/root/")
    for obj in result:
        if obj[0] != '.':
            result = obj
            break
        else:
            result = 'None'
    sftp.close()
    return result


def scp_detect_outdated_firmware(host, user, secret, project, source):
    transport = paramiko.Transport((host, 22))
    transport.connect()
    transport.auth_none(username=user)
    sftp = core.MySFTPClient.from_transport(transport)
    local_firmware = os.stat('%s/Build/bin/%s.bin' % (source, project))
    device_firmware = sftp.lstat('/home/root/%s/bin/%s.bin' % (project, project))
    sftp.close()
    if device_firmware.st_mtime < float(local_firmware.st_mtime):
        return -1  # outdated
    elif device_firmware.st_mtime < float(local_firmware.st_mtime):
        return 1  # newer
    elif device_firmware.st_mtime == float(local_firmware.st_mtime):
        return 0  # similar

