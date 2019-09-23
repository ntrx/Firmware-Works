#!/usr/bin/env python
# list of functions for scripts
import os
import settings
import paramiko
import core
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
    return os.system("\"%s\" /ini=nul /script=%s" % (winscp_path, file_name))


def putty_path(host, user, path_putty=PATH_PUTTY):
    CREATE_NO_WINDOW = 0x08000000
    return subprocess.Popen("\"%s\" -ssh %s@%s" % (path_putty, user, host), creationflags=CREATE_NO_WINDOW)


def scp_upload(source, project, user, secret, host):
    path_loc_win = source + "\\Build\\bin\\" + project + ".bin"
    path_dest_win = "//home//" + user + "//" + project + "//bin//" + project + ".bin"
    if SETTINGS_FTP_MODE == '1' or '0':
        file_name = 'upload' + host
        f = open(file_name, "w+")
        f.write("option confirm off\n")
        f.write("open sftp://%s:%s@%s/ -hostkey=*\n" % (user, secret, host))
        f.write("put %s %s\n" % (path_loc_win, path_dest_win))
        f.write("exit\n")
        f.close()
        scp_path(file_name, PATH_WINSCP)
        os.remove(file_name)
    elif SETTINGS_FTP_MODE == '2':
        transport = paramiko.Transport(host, 22)
        transport.connect(username=user, password=secret)
        sftp = core.MySFTPClient.from_transport(transport)
        sftp.put(path_loc_win, path_dest_win)
        sftp.close()


def scp_killall(user, secret, host, project):
    if SETTINGS_FTP_MODE == '1' or '0':  # via winSCP
        file_name = 'killall' + host
        f = open(file_name, "w+")
        f.write("option confirm off\n")
        f.write("open sftp://%s:%s@%s/ -hostkey=*\n" % (user, secret, host))
        f.write("call killall sn4215_respawn.sh %s.bin\n" % project)
        f.write("exit\n")
        f.close()
        scp_path(file_name, PATH_WINSCP)
        os.remove(file_name)
    if SETTINGS_FTP_MODE == '2':  # via paramiko
        paramiko.util.log_to_file('killall_command.log')
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(host, 22, user, secret)
        client.exec_command("killall sn4215_respawn.sh %s.bin" % project)
        client.close()


def scp_reboot(user, secret, host):
    if SETTINGS_FTP_MODE == '1' or '0':  # via winSCP
        file_name = 'reboot' + host
        f = open(file_name, "w+")
        f.write("option confirm off\n")
        f.write("open sftp://%s:%s@%s/ -hostkey=*\n" % (user, secret, host))
        f.write("call shutdown -r now\n")
        f.write("exit\n")
        f.close()
        scp_path(file_name, PATH_WINSCP)
        os.remove(file_name)
    if SETTINGS_FTP_MODE == '2':  # via paramiko
        paramiko.util.log_to_file('reboot_command.log')
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(host, 22, user, secret)
        client.exec_command("shutdown -r now")
        client.close()


def scp_poweroff(user, secret, host):
    if SETTINGS_FTP_MODE == '1' or '0':  # via winSCP
        file_name = 'poweroff' + host
        f = open(file_name, "w+")
        f.write("option confirm off\n")
        f.write("open sftp://%s:%s@%s/ -hostkey=*\n" % (user, secret, host))
        f.write("call poweroff\n")
        f.write("exit\n")
        f.close()
        scp_path(file_name, PATH_WINSCP)
        os.remove(file_name)
    if SETTINGS_FTP_MODE == '2':  # via paramiko
        paramiko.util.log_to_file('poweroff_command.log')
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(host, 22, user, secret)
        client.exec_command("poweroff")
        client.close()


def scp_ts_test(user, secret, host):
    if SETTINGS_FTP_MODE == '1' or '0':  # via winSCP
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
    if SETTINGS_FTP_MODE == '2':  # via paramiko
        paramiko.util.log_to_file('ts_test_command.log')
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(host, 22, user, secret)
        client.exec_command("/etc/init.d/autorun.sh stop")
        client.exec_command("TSLIB_TSDEVICE=/dev/input/event2 ts_test")
        client.close()


def scp_ts_calibrate(user, secret, host):
    if SETTINGS_FTP_MODE == '1' or '0':  # via winSCP
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
    if SETTINGS_FTP_MODE == '2':  # via paramiko
        paramiko.util.log_to_file('ts_calibrate_command.log')
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(host, 22, user, secret)
        client.exec_command("/etc/init.d/autorun.sh stop")
        client.exec_command("TSLIB_TSDEVICE=/dev/input/event2 ts_calibrate")
        client.close()


def scp_stop(user, secret, host):
    if SETTINGS_FTP_MODE == '1' or '0':  # via winSCP
        file_name = 'stop' + host
        f = open(file_name, "w+")
        f.write("option confirm off\n")
        f.write("open sftp://%s:%s@%s/ -hostkey=*\n" % (user, secret, host))
        f.write("call /etc/init.d/autorun.sh stop\n")
        f.write("exit\n")
        f.close()
        scp_path(file_name)
        os.remove(file_name)
    if SETTINGS_FTP_MODE == '2':  # via paramiko
        paramiko.util.log_to_file('stop_command.log')
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(host, 22, user, secret)
        client.exec_command("/etc/init.d/autorun.sh stop")
        client.close()


def scp_restart(user, secret, host):
    file_name = 'restart' + host
    if SETTINGS_FTP_MODE == '1' or '0':  # via winSCP
        f = open(file_name, "w+")
        f.write("option confirm off\n")
        f.write("open sftp://%s:%s@%s/ -hostkey=*\n" % (user, secret, host))
        f.write("call /etc/init.d/autorun.sh restart\n")
        f.write("exit\n")
        f.close()
        scp_path(file_name)
        os.remove(file_name)
    if SETTINGS_FTP_MODE == '2':  # via paramiko
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


# return 1 if online
def is_online(host, times=1):
    ping_status = subprocess.call("ping -n %d %s" % (times, host))
    if ping_status == 0:  # active
        return 1
    elif ping_status > 0:
        return 0
    elif ping_status < 0:
        return 0
    else:
        return 0


# isUpdate = 1 :: files already been on SERVER (SYNC, faster)
# isUpdate = 0 :: no file on server, its first upload
# build (release or debug type)
def scp_compile(source, user, secret, project, is_update, build='release'):
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
