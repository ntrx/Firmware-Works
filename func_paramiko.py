#!/usr/bin/env python
# Using module paramiko for perform scp/sftp actions
import os
import paramiko
import subprocess
from scp import SCPClient
import fs
from core import MySFTPClient


def createSSHClient(server, port, user, secret):
    """
    Creating SSH Client for perform SSH commands

    :param server: server ip address
    :type server: str
    :param port: server port
    :type port: int
    :param user: login username
    :type user: str
    :param secret: username password
    :type secret: str
    :return: client object
    """
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


def para_upload(Settings):
    """
    Upload firmware binary file to device by sFTP, added 777 rights to file.

    :param Settings: configuration
    :return: None
    """
    path_loc_win = Settings.project.path_local + "\\Build\\bin\\" + Settings.project.name + ".bin"
    path_dest_win = "//home//" + Settings.device.user + "//" + Settings.project.name + "//bin//" + Settings.project.name + ".bin"
    transport = paramiko.Transport((Settings.device.ip, 22))
    transport.connect()
    transport.auth_none(username=Settings.device.user)
    sftp = MySFTPClient.from_transport(transport)
    sftp.rename(path_dest_win, path_dest_win + "_backup")
    sftp.put(path_loc_win, path_dest_win)
    sftp.chmod(path_dest_win, 777)
    sftp.close()


def para_killall(Settings):
    """
    Using autorun.sh on device by SSH to launch killall command

    :param Settings: configuration
    :return: None
    """
    paramiko.util.log_to_file('killall_command.log')
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=Settings.device.ip, port=22, username=Settings.device.user, password=Settings.device.password)
    client.exec_command("killall sn4215_respawn.sh %s.bin" % Settings.project.name)
    client.close()


def para_reboot(Settings):
    """
    Perform reboot command on device (SSH)

    :param Settings: configuration
    :return: None
    """
    paramiko.util.log_to_file('reboot_command.log')
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(Settings.device.ip, 22, Settings.device.user, Settings.device.password)
    client.exec_command("sudo reboot")
    client.close()


def para_poweroff(Settings):
    """
    Perform shutdown command on device (SSH)

    :param Settings: configuration
    :return: None
    """
    paramiko.util.log_to_file('poweroff_command.log')
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(Settings.device.ip, 22, Settings.device.user, Settings.device.password)
    client.exec_command("poweroff")
    client.close()


def para_ts_test(Settings):
    """
    Using autorun.sh to launch test app after calibration (SSH)

    :param Settings: configuration
    :return: None
    """
    paramiko.util.log_to_file('ts_test_command.log')
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(Settings.device.ip, 22, Settings.device.user, Settings.device.password)
    client.exec_command("/etc/init.d/autorun.sh stop")
    client.exec_command("TSLIB_TSDEVICE=/dev/input/event2 ts_test")
    client.close()


def scp_ts_calibrate(Settings):
    """
    Using autorun.sh to launch touchscreen calibration app (SSH)

    :param Settings: configuration
    :return: None
    """
    paramiko.util.log_to_file('ts_calibrate_command.log')
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(Settings.device.ip, 22, Settings.device.user, Settings.device.password)
    client.exec_command("/etc/init.d/autorun.sh stop")
    client.exec_command("TSLIB_TSDEVICE=/dev/input/event2 ts_calibrate")
    client.close()


def para_stop(Settings):
    """
    Using autorun.sh to stop firmware process on device (SSH)

    :param Settings: configuration
    :return: None
    """
    paramiko.util.log_to_file('stop_command.log')
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(Settings.device.ip, 22, Settings.device.user, Settings.device.password)
    client.exec_command("/etc/init.d/autorun.sh stop")
    client.close()


def para_restart(Settings):
    """
    Using autorun.sh to restart firmware on device (SSH)

    :param Settings: configuration
    :return: None
    """
    paramiko.util.log_to_file('restart_command.log')
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    if Settings.device.password == '':
        print('using no password')
        client.connect(hostname=Settings.device.ip, port=22, username=Settings.device.user)
    else:
        print('using password')
        client.connect(Settings.device.ip, 22, Settings.device.user, Settings.device.password)
    print('do')
    client.exec_command("/etc/init.d/autorun.sh restart")
    client.close()


def para_rmdir(Settings):
    """
    Removing DIR on external server (SSH)

    :param Settings: configuration
    :return: None
    """
    path_dest_win = "//home//" + Settings.server.user + Settings.server.path_external
    paramiko.util.log_to_file('rmdir.log')
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(Settings.server.ip, 22, Settings.server.user, Settings.server.password)
    stdin, stdout, stderr = client.exec_command("rmdir " + path_dest_win)
    data = stdout.read() + stderr.read()
    i = 0
    while i < len(data):
        print(chr(data[i]), end="")
        i += 1
    client.close()


def para_compile(Settings, build):
    """
    Upload sources from local dir and compiling firmware on server or device builtin compiler

    :param Settings: configuration
    :param build: release or debug mode
    :type build: str
    :return: None
    """
    if os.name == 'nt': # if Windows
        if Settings.device.system == 0:  # NXP iMX6
            path_loc_win = Settings.project.path_local  # os.getcwd()
            path_dest_win = "//home//" + Settings.server.user + Settings.server.path_external
            if not os.path.exists(fs.path_double_win(path_loc_win + "\\Build\\bin\\")):
                os.mkdir(path=fs.path_double_win(path_loc_win + "\\Build\\bin\\"))
            transport = paramiko.Transport(Settings.server.ip, 22)
            transport.connect(username=Settings.server.user, password=Settings.server.password)
            sftp = MySFTPClient.from_transport(transport)
            if Settings.server.sync_files == '0':
                sftp.mkdir(path_dest_win, ignore_existing=True)
                sftp.mkdir(path_dest_win + '/Src', ignore_existing=True)
                sftp.mkdir(path_dest_win + '/Build', ignore_existing=True)
                sftp.put_dir(path_loc_win + '\\Src', path_dest_win + '/Src/')
            elif Settings.server.sync_files == '1':
                pass
            else:
                pass

            paramiko.util.log_to_file('compile.log')
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            client.connect(Settings.server.ip, 22, Settings.server.user, Settings.server.password)

            if Settings.server.sync_files == '0':
                stdin, stdout, stderr = client.exec_command("make -C /home/" + Settings.server.user + Settings.server.path_external + "/Src clean")
                data = stdout.read() + stderr.read()
                stdin, stdout, stderr = client.exec_command(" make " + Settings.server.compiler + " -C /home/" + Settings.server.user + Settings.server.path_external + "/Src -j7 --makefile=Makefile")
                data += stdout.read() + stderr.read()
            elif Settings.server.sync_files == '1':
                stdin, stdout, stderr = client.exec_command("make " + Settings.server.compiler + " -C /home/" + Settings.server.user + Settings.server.path_external + "/Src -j7")
                data = stdout.read() + stderr.read()
            i = 0
            while i < len(data):
                print(chr(data[i]), end="")
                i += 1
            client.close()

            path_loc_nix = "/home/%s%s/Build/bin/%s.bin" % (Settings.server.user, Settings.server.path_external, Settings.project.name)
            path_loc_nix = fs.path_double_nix(path_loc_nix)
            print("Getting file: ", path_loc_nix)
            path_loc_win = fs.path_double_win(Settings.project.path_local)
            sftp.get(remotepath=path_loc_nix, localpath=path_loc_win + "\\Build\\bin\\" + Settings.project.name + ".bin")
            print("Saving to: " + path_loc_win + "\\Build\\bin\\" + Settings.project.name + ".bin")
            sftp.close()
        elif Settings.device.system == 1:  # Intel Atom
            path_loc_win = Settings.project.path_local  # os.getcwd()
            path_dest_win = Settings.server.path_external
            file_name = 'compile' + Settings.project.name
    else: # if Linux
        if Settings.device.system == 0:  # NXP iMX6
            if Settings.server.using:  # Build-server
                path_loc_nix = Settings.project.path_local
                path_dest_nix = "//home//" + Settings.server.user + Settings.server.path_external
                if not os.path.exists(fs.path_double_nix(path_loc_nix + "//Build//bin//")):
                    os.mkdir(path=fs.path_double_nix(path_loc_nix + "//Build//bin//"))
                if True:
                    transport = paramiko.Transport(Settings.server.ip, 22)
                    transport.connect(username=Settings.server.user, password=Settings.server.password)
                    sftp = MySFTPClient.from_transport(transport)
                    if Settings.server.sync_files == '0':
                        sftp.mkdir(path_dest_nix, ignore_existing=True)
                        sftp.mkdir(path_dest_nix + '/Src', ignore_existing=True)
                        sftp.mkdir(path_dest_nix + '/Build', ignore_existing=True)
                        sftp.put_dir(path_loc_nix + '//Src', path_dest_nix + '/Src/')
                    elif Settings.server.sync_files == '1':
                        pass
                    else:
                        pass

                    paramiko.util.log_to_file('compile.log')
                    client = paramiko.SSHClient()
                    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                    client.connect(Settings.server.ip, 22, Settings.server.user, Settings.server.password)

                    if Settings.server.sync_files == '0':
                        stdin, stdout, stderr = client.exec_command("make -C /home/" + Settings.server.user + Settings.server.path_external + "/Src clean")
                        data = stdout.read() + stderr.read()
                        stdin, stdout, stderr = client.exec_command(" make " + Settings.server.compiler + " -C /home/" + Settings.server.user + Settings.server.path_external + "/Src -j7 --makefile=Makefile")
                        data += stdout.read() + stderr.read()
                    elif Settings.server.sync_files == '1':
                        stdin, stdout, stderr = client.exec_command("make " + Settings.server.compiler + " -C /home/" + Settings.server.user + Settings.server.path_external + "/Src -j7")
                        data = stdout.read() + stderr.read()
                    i = 0
                    while i < len(data):
                        print(chr(data[i]), end="")
                        i += 1
                    client.close()

                    path_loc_dest = '/home/%s%s/Build/bin/%s.bin' % (Settings.server.user, Settings.server.path_external, Settings.project.name)
                    path_loc_dest = fs.path_double_nix(path_loc_dest)
                    print("Getting file:", path_loc_dest)
                    path_loc_nix = fs.path_double_nix(Settings.project.path_local)
                    sftp.get(remotepath=path_loc_dest, localpath=path_loc_nix + "/Build/bin/" + Settings.project.name + '.bin')
                    print('Saving file to:' + path_loc_nix + '/Build/bin/' + Settings.project.name + '.bin')
                    sftp.close()


def para_detect_project(Settings, self):
    """
    Detect project available on device (correctly work only if on device available one project)

    :param Settings: configuration
    :param self: activity
    :return: None
    """
    if Settings.device.file_protocol == 'sftp':
        transport = paramiko.Transport((Settings.device.ip, 22))
        transport.connect()
        transport.auth_none(username=Settings.device.user)
        sftp = MySFTPClient.from_transport(transport)
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
            transport = paramiko.Transport((Settings.device.ip, 22))
            transport.connect()
            transport.auth_none(username=Settings.device.user)
            sftp = MySFTPClient.from_transport(transport)
            result = sftp.listdir("/home/root/")
            for obj in result:
                if obj[0] != '.':
                    result = obj
                    break
                else:
                    result = 'None'
            sftp.close()
            self.setText("Detected firmware: %s" % result)


def para_detect_outdated_firmware(Settings, self):
    """
    Getting firmware from device and checking it with last compiled firmware

    :param Settings: configuration
    :param self: activity
    :return: None
    """
    local_firmware = os.stat('%s/Build/bin/%s.bin' % (Settings.project.path_local, Settings.project.name))
    if Settings.device.file_protocol == 'sftp':
        transport = paramiko.Transport((Settings.device.ip, 22))
        transport.connect()
        transport.auth_none(username=Settings.device.user)
        sftp = MySFTPClient.from_transport(transport)
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


def para_psplash_upload(Settings, self):
    """
    Upload psplash file with preset location to device by sFTP

    :param Settings: configuration
    :param self: activity
    :return: None
    """
    file_name = fs.path_get_filename(Settings.project.path_psplash)
    path_dest = "//usr//bin//" + file_name
    path_loc_win = Settings.project.path_psplash
    transport = paramiko.Transport((Settings.device.ip, 22))
    transport.connect()
    transport.auth_none(username=Settings.device.user)
    sftp = MySFTPClient.from_transport(transport)
    sftp.put(path_loc_win, path_dest)
    sftp.chmod(path_dest, 777)
    sftp.close()
    self.setText("psplash command sent")


def para_clean(Settings):
    """
    Perform 'make clean' to sources on build-server (sFTP)

    :param Settings:
    :return:
    """
    if os.name == 'nt':
        transport = paramiko.Transport(Settings.server.ip, 22)
        transport.connect(username=Settings.server.user, password=Settings.server.password)
        sftp = MySFTPClient.from_transport(transport)

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
        path_loc_nix = Settings.project.path_local
        if not os.path.exists(fs.path_double_nix(path_loc_nix + "//Build//bin//")):
            return
        if True:
            paramiko.util.log_to_file('clean.log')
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            client.connect(Settings.server.ip, 22, Settings.server.user, Settings.server.password)

            stdin, stdout, stderr = client.exec_command("make -C /home/" + Settings.server.user + Settings.server.path_external + "/Src clean")
            data = stdout.read() + stderr.read()

            i = 0
            while i < len(data):
                print(chr(data[i]), end="")
                i += 1
            client.close()
            

def sftp_callback(transferred, toBeTransferred):
    print("Transferred: {0}\tOut of: {1}".format(transferred, toBeTransferred))
