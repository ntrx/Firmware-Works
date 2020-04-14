#!/usr/bin/env python
# Using module paramiko for perform scp/sftp actions

from core import _SYNC_FILES_
from core import _UPLOAD_FILES_
from core import _SFTP_
from core import _SCP_
from core import _NXP_
from core import _ATOM_

import os
import paramiko
from scp import SCPClient
import fs
import func


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


class MySFTPClient(paramiko.SFTPClient):
    def put_dir(self, source, target):
        for item in os.listdir(source):
            if os.path.isfile(os.path.join(source, item)):
                if item.find('.ipch') >= 0 or item.find('.obj') >= 0 or item.find('.exe') >= 0:
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


class MySCPClient(SCPClient):
    def put_dir(self, source, target):
        for item in os.listdir(source):
            if os.path.isfile(os.path.join(source, item)):
                self.put(os.path.join(source, item), '%s/%s' % (target, item))
            else:
                self.put_dir(os.path.join(source, item), '%s/%s' % (target, item))


def upload(Settings):
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


def killall(Settings):
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


def reboot(Settings):
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


def poweroff(Settings):
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


def ts_test(Settings):
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


def ts_calibrate(Settings):
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


def stop(Settings):
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


def restart(Settings):
    """
    Using autorun.sh to restart firmware on device (SSH)

    :param Settings: configuration
    :return: None
    """
    paramiko.util.log_to_file('restart_command.log')
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(Settings.device.ip, 22, Settings.device.user, Settings.device.password)
    client.exec_command("/etc/init.d/autorun.sh restart")
    client.close()


def rmdir(Settings):
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
    func.prompt_print(data)
    client.close()


def make(Settings, build):
    """
    Upload sources from local dir and compiling firmware on server or device builtin compiler

    :param Settings: configuration
    :param build: release or debug mode
    :type build: str
    :return: None
    """
    if Settings.device.system == _NXP_:  # NXP iMX6
        path_loc_win = Settings.project.path_local  # os.getcwd()
        path_dest_win = "//home//" + Settings.server.user + Settings.server.path_external
        if not os.path.exists(fs.path_double_win(path_loc_win + "\\Build\\bin\\")):
            os.mkdir(path=fs.path_double_win(path_loc_win + "\\Build\\bin\\"))
        transport = paramiko.Transport(Settings.server.ip, 22)
        transport.connect(username=Settings.server.user, password=Settings.server.password)
        sftp = MySFTPClient.from_transport(transport)
        if Settings.server.sync_files == _UPLOAD_FILES_:
            sftp.mkdir(path_dest_win, ignore_existing=True)
            sftp.mkdir(path_dest_win + '/Src', ignore_existing=True)
            sftp.mkdir(path_dest_win + '/Build', ignore_existing=True)
            sftp.put_dir(path_loc_win + '\\Src', path_dest_win + '/Src/')
        elif Settings.server.sync_files == _SYNC_FILES_:
            pass

        paramiko.util.log_to_file('compile.log')
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(Settings.server.ip, 22, Settings.server.user, Settings.server.password)

        if Settings.server.sync_files == _UPLOAD_FILES_:
            stdin, stdout, stderr = client.exec_command("make -C /home/" + Settings.server.user + Settings.server.path_external + "/Src clean")
            data = stdout.read() + stderr.read()
            if build == 'release':
                stdin, stdout, stderr = client.exec_command(" make " + Settings.server.compiler + " -C /home/" + Settings.server.user + Settings.server.path_external + "/Src -j7 --makefile=Makefile")
                data += stdout.read() + stderr.read()
            elif build == 'debug':
                stdin, stdout, stderr = client.exec_command(" make " + Settings.server.compiler + " debug -C /home/" + Settings.server.user + Settings.server.path_external + "/Src -j7 --makefile=Makefile")
                data += stdout.read() + stderr.read()
        elif Settings.server.sync_files == _SYNC_FILES_:
            if build == 'release':
                stdin, stdout, stderr = client.exec_command("make " + Settings.server.compiler + " -C /home/" + Settings.server.user + Settings.server.path_external + "/Src -j7")
            elif build == 'debug':
                stdin, stdout, stderr = client.exec_command("make debug" + Settings.server.compiler + " -C /home/" + Settings.server.user + Settings.server.path_external + "/Src -j7")
            data = stdout.read() + stderr.read()
        func.prompt_print(data)
        client.close()

        path_loc_nix = "/home/%s%s/Build/bin/%s.bin" % (Settings.server.user, Settings.server.path_external, Settings.project.name)
        path_loc_nix = fs.path_double_nix(path_loc_nix)
        print("Getting file: ", path_loc_nix)
        path_loc_win = fs.path_double_win(Settings.project.path_local)
        sftp.get(remotepath=path_loc_nix, localpath=path_loc_win + "\\Build\\bin\\" + Settings.project.name + ".bin")
        print("Saving to: " + path_loc_win + "\\Build\\bin\\" + Settings.project.name + ".bin")
        sftp.close()
    elif Settings.device.system == _ATOM_:  # Intel Atom
        path_loc_win = Settings.project.path_local  # os.getcwd()
        path_dest_win = Settings.server.path_external

        transport = paramiko.Transport(Settings.device.ip, 22)
        transport.connect(username=Settings.device.user, password=Settings.device.password)
        sftp = MySFTPClient.from_transport(transport)
        if Settings.server.sync_files == _UPLOAD_FILES_:
            sftp.mkdir(Settings.server.path_external)
            sftp.put_dir(path_loc_win + '\\Src', path_dest_win + '/Src/')
        elif Settings.server.sync_files == _SYNC_FILES_:
            pass

        paramiko.util.log_to_file('compile.log')
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(Settings.device.ip, 22, Settings.device.user, Settings.device.password)

        if Settings.server.sync_files == _UPLOAD_FILES_:
            stdin, stdout, stderr = client.exec_command("make -C /" + Settings.server.path_external + "/Src clean")
            data = stdout.read() + stderr.read()
            if build == 'release':
                stdin, stdout, stderr = client.exec_command("make " + Settings.server.compiler + " -C /" + Settings.server.path_external + "/Src --makefile=Makefile")
            elif build == 'debug':
                stdin, stdout, stderr = client.exec_command("make " + Settings.server.compiler + " debug -C /" + Settings.server.path_external + "/Src --makefile=Makefile")
            data += stdout.read() + stderr.read()
        elif Settings.server.sync_files == _SYNC_FILES_:
            if build == 'release':
                stdin, stdout, stderr = client.exec_command("make " + Settings.server.compiler + " -C /" + Settings.server.path_external + "/Src ")
            elif build == 'debug':
                stdin, stdout, stderr = client.exec_command("make debug" + Settings.server.compiler + " -C /" + Settings.server.path_external + "/Src ")
            data = stdout.read() + stderr.read()
        func.prompt_print(data)

        stdin, stdout, stderr = client.exec_command("mv //root//navigation//bin//%s.bin //root//navigation//bin//%s.bin-backup")
        data = stdout.read() + stderr.read()
        stdin, stdout, stderr = client.exec_command("mv //root//%s//Build//bin//%s.bin //root//navigation//bin//%s.bin" % (Settings.server.path_external, Settings.project.name, Settings.project.name))
        data += stdout.read() + stderr.read()
        func.prompt_print(data)

        client.close()
        sftp.close()


def detect_project(Settings, self):
    """
    Detect project available on device (correctly work only if on device available one project)

    :param Settings: configuration
    :param self: activity
    :return: None
    """
    if Settings.device.file_protocol == _SFTP_:
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
    elif Settings.device.file_protocol == _SCP_:
        pass


def detect_outdated_firmware(Settings, self):
    """
    Getting firmware from device and checking it with last compiled firmware

    :param Settings: configuration
    :param self: activity
    :return: None
    """
    local_firmware = os.stat('%s/Build/bin/%s.bin' % (Settings.project.path_local, Settings.project.name))
    if Settings.device.file_protocol == _SFTP_:
        transport = paramiko.Transport((Settings.device.ip, 22))
        transport.connect()
        transport.auth_none(username=Settings.device.user)
        sftp = MySFTPClient.from_transport(transport)
        device_firmware = sftp.lstat('/home/root/%s/bin/%s.bin' % (Settings.project.name, Settings.project.name))
        sftp.close()
    elif Settings.device.file_protocol == _SCP_:
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


def psplash_upload(Settings, self):
    """
    Upload psplash file with preset location to device by sFTP

    :param Settings: configuration
    :param self: activity
    :return: None
    """
    if Settings.device.file_protocol == _SFTP_:
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
    elif Settings.device.file_protocol == _SCP_:
        pass
    self.setText("psplash command sent")


def clean(Settings):
    """
    Perform 'make clean' to sources on build-server (sFTP)

    :param Settings:
    :return:
    """
    path_loc_nix = Settings.project.path_local
    if not os.path.exists(fs.path_double_nix(path_loc_nix + "//Build//bin//")):
        return

    paramiko.util.log_to_file('clean.log')
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(Settings.server.ip, 22, Settings.server.user, Settings.server.password)
    stdin, stdout, stderr = client.exec_command("make -C /home/" + Settings.server.user + Settings.server.path_external + "/Src clean")
    data = stdout.read() + stderr.read()
    func.prompt_print(data)
    client.close()


def sftp_callback(transferred, toBeTransferred):
    print("Transferred: {0}\tOut of: {1}".format(transferred, toBeTransferred))
