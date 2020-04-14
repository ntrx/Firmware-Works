#!/usr/bin/env python
# Using external apps on linux systems
import os
import fs


def upload(Settings):
    """
    Upload firmware binary file to device by SFTP or SCP, added 777 rights to file if using sFTP.

    :param Settings: configuration
    :return: None
    """
    file_name = 'upload' + Settings.device.ip
    path_loc_nix = Settings.project.path_local + "//Build//bin//" + Settings.project.name + ".bin"
    path_dest_nix = "//home//" + Settings.device.user + "//" + Settings.project.name + "//bin//"
    if Settings.device.file_protocol == 'sftp': # sftp, not tested
        f = open(file_name, "w+")
        f.write("sftp %s@%s << EOF\n" % (Settings.device.user, Settings.device.ip))
        f.write("rename %s %s_backup\n" % (path_loc_nix, path_dest_nix))
        f.write("put %s %s\n" % (path_loc_nix, path_dest_nix))
        f.write("EOF\n")
        f.close()
        os.system("chmod 777 %s" % file_name)
        os.system("%s" % file_name)
        os.remove(file_name)
    elif Settings.device.file_protocol == 'scp': # scp
        os.system("scp %s %s@%s:%s" % (path_loc_nix, Settings.device.user, Settings.device.ip, path_dest_nix))


def killall(Settings):
    """
    Using autorun.sh on device by ssh to launch killall command

    :param Settings: configuration
    :return: None
    """
    os.system("ssh %s@%s 'killall sn4215_respawn.sh %s.bin | exit'" % (Settings.device.user, Settings.device.ip, Settings.project.name))


def reboot(Settings):
    """
    Perform reboot command on device by SSH

    :param Settings: configuration
    :return: None
    """
    os.system("ssh %s@%s 'sudo reboot | exit'" % (Settings.device.user, Settings.device.ip))


def poweroff(Settings):
    """
    Perform shutdown command on device by SSH

    :param Settings: configuration
    :return: None
    """
    os.system("ssh %s@%s 'poweroff | exit'" % (Settings.device.user, Settings.device.ip))


def ts_test(Settings):
    """
    Using autorun.sh to launch test app after calibration (SSH)

    :param Settings: configuration
    :return: None
    """
    os.system("ssh %s@%s '/etc/init.d/autorun.sh stop | TSLIB_TSDEVICE=/dev/input/event2 ts_test | exit'" % (Settings.device.user, Settings.device.ip))


def ts_calibrate(Settings):
    """
    Using autorun.sh to launch touchscreen calibration app (SSH)

    :param Settings: configuration
    :return: None
    """
    os.system("ssh %s@%s '/etc/init.d/autorun.sh stop | TSLIB_TSDEVICE=/dev/input/event2 ts_calibrate | exit'" % (Settings.device.user, Settings.device.ip))


def stop(Settings):
    """
    Using autorun.sh to stop firmware process on device (SSH)

    :param Settings: configuration
    :return: None
    """
    os.system("ssh %s@%s '/etc/init.d/autorun.sh stop | exit'" % (Settings.device.user, Settings.device.ip))


def restart(Settings):
    """
    Using autorun.sh to restart firmware on device (SSH)

    :param Settings: configuration
    :return: None
    """
    os.system("ssh %s@%s '/etc/init.d/autorun.sh restart | exit'" % (Settings.device.user, Settings.device.ip))


def rmdir(Settings):
    # see para_rmdir
    return


def make(Settings, build):
    # see para_compile
    return


def psplash_upload(Settings, self):
    """
    Upload psplash file with preset location to device by sFTP

    :param Settings: configuration
    :param self: activity
    :return: None
    """
    file_name = fs.path_get_filename(Settings.project.path_psplash)
    path_dest = "//usr//bin//" + file_name
    script_file = 'psplash' + Settings.device.ip
    path_loc_nix = Settings.project.path_psplash
    if Settings.device.file_protocol == 'sftp':
        f = open(script_file, "w+")
        f.write("sftp %s@%s << EOF\n" % (Settings.device.user, Settings.device.ip))
        f.write("rename %s %s_backup\n" % (path_loc_nix, path_dest))
        f.write("put %s %s\n" % (path_loc_nix, path_dest))
        f.write("EOF\n")
        f.close()
        os.system("chmod 777 %s" % script_file)
        os.system("%s" % script_file)
    elif Settings.device.file_protocol == 'scp':
        os.system("scp %s %s@%s:%s" % (path_loc_nix, Settings.device.user, Settings.device.ip, path_dest))
    self.setText("SENT: psplash upload command.")


def clean(Settings):
 # see para_clean
    return
