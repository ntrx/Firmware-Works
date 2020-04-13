#!/usr/bin/env python
# Scripts for WinSCP for devices and external servers
import os
import subprocess
import fs


def winscp_path(file_name, path):
    """
    Launches file (script) to WinSCP executable.

    :param file_name: script file name
    :type file_name: str
    :param path: loc to winscp.com or winscp.exe
    :type path: str
    :return: 0, if successfully
    """
    return os.system("\"%s\" /ini=nul /script=%s" % (path, file_name))


def command(arguments, path):
    """
    Launches not attached WinSCP script

    :param arguments: commands list
    :type arguments: str
    :param path: Path to WinSCP
    :type path: str
    :return: None
    """
    CREATE_NO_WINDOW = 0x08000000
    return subprocess.Popen("\"%s\" %s" % (path, arguments), creationflags=CREATE_NO_WINDOW)


def putty_path(host, user, path):
    """
    Opening Putty window which is not attached

    :param host: IP
    :type host: str
    :param user: user name
    :type user: str
    :param path: path to putty
    :type path: str
    :return: None
    """
    CREATE_NO_WINDOW = 0x08000000
    return subprocess.Popen("\"%s\" -ssh %s@%s" % (path, user, host), creationflags=CREATE_NO_WINDOW)


def upload(Settings):
    """
    Upload firmware binary file to device by sFTP or SCP protocols, added 777 rights to file.

    :param Settings: configuration
    :return: None
    """
    file_name = 'upload' + Settings.device.ip
    path_loc_win = Settings.project.path_local + "\\Build\\bin\\" + Settings.project.name + ".bin"
    path_dest_win = "//home//" + Settings.device.user + "//" + Settings.project.name + "//bin//" + Settings.project.name + ".bin"
    f = open(file_name, "w+")
    f.write("option confirm off\n")
    if Settings.device.file_protocol == 'sftp':
        f.write("open sftp://%s:%s@%s/ -hostkey=*\n" % (Settings.device.user, Settings.device.password, Settings.device.ip))
    elif Settings.device.file_protocol == 'scp':
        f.write("open scp://%s@%s:%s/ -hostkey=*\n" % (Settings.device.user, Settings.device.ip, Settings.device.password))
    f.write("cp %s %s_backup\n" % (path_dest_win, path_dest_win))
    f.write("put %s %s\n" % (path_loc_win, path_dest_win))
    f.write("chmod 777 \"%s\"\n" % path_dest_win)
    f.write("exit\n")
    f.close()
    winscp_path(file_name, Settings.local.path_winscp)
    os.remove(file_name)
    

def killall(Settings):
    """
    Using autorun.sh on device by sFTP/SCP protocol to launch killall command.

    :param Settings: configuration
    :return: None
    """
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
    winscp_path(file_name, Settings.local.path_winscp)
    os.remove(file_name)
      

def reboot(Settings):
    """
    Perform reboot command on device (SCP/sFTP protocol)

    :param Settings: configuration
    :return: None
    """
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
    winscp_path(file_name, Settings.local.path_winscp)
    os.remove(file_name)


def poweroff(Settings):
    """
    Perform shutdown command on device (SCP/sFTP)

    :param Settings: configuration
    :return: None
    """
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
    winscp_path(file_name, Settings.local.path_winscp)
    os.remove(file_name)


def ts_test(Settings):
    """
    Using autorun.sh to launch test app after calibration (SCP/sFTP)

    :param Settings: configuration
    :return: None
    """
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
    winscp_path(file_name, Settings.local.path_winscp)
    os.remove(file_name)
       

def ts_calibrate(Settings):
    """
    Using autorun.sh to launch touchscreen calibration app (SCP/sFTP)

    :param Settings: configuration
    :return: None
    """
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
    winscp_path(file_name, Settings.local.path_winscp)
    os.remove(file_name)


def stop(Settings):
    """
    Using autorun.sh to stop firmware process on device (SCP/sFTP)

    :param Settings: configuration
    :return: None
    """
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
    winscp_path(file_name, Settings.local.path_winscp)
    os.remove(file_name)


def restart(Settings):
    """
    Using autorun.sh to restart firmware on device (SCP/sFTP)

    :param Settings: configuration
    :return: None
    """
    file_name = 'restart' + Settings.device.ip
    f = open(file_name, "w+")
    f.write("option confirm off\n")
    if Settings.device.file_protocol == 'sftp':
        f.write("open sftp://%s:%s@%s/ -hostkey=*\n" % (Settings.device.user, Settings.device.password, Settings.device.ip))
    elif Settings.device.file_protocol == 'scp':
        f.write("open scp://%s@%s:%s/ -hostkey=*\n" % (Settings.device.user, Settings.device.ip, Settings.device.password))
    f.write("call /etc/init.d/autorun.sh restart\n")
    f.write("exit\n")
    f.close()
    winscp_path(file_name, Settings.local.path_winscp)
    os.remove(file_name)


def rmdir(Settings):
    """
    Removing DIR on external server (SFTP)

    :param Settings: configuration
    :return: None
    """
    path_dest_win = "//home//" + Settings.server.user + Settings.server.path_external
    file_name = 'rmdir' + Settings.project.name
    f = open(file_name, 'w+')
    f.write("option confirm off\n")
    f.write("open sftp://%s:%s@%s/ -hostkey=*\n" % (Settings.server.user, Settings.server.password, Settings.server.ip))
    f.write("rmdir %s\n" % path_dest_win)
    f.write("exit\n")
    f.close()
    winscp_path(file_name, Settings.local.path_winscp)
    os.remove(file_name)


def compile(Settings, build):
    """
    Upload/sync sources with local dir and compiling firmware on server or device builtin compiler

    :param Settings: configuration
    :param build: release or debug mode
    :type build: str
    :return: None
    """
    if Settings.device.system == 0:  # NXP iMX6
        path_loc_win = Settings.project.path_local  # os.getcwd()
        path_dest_win = "//home//" + Settings.server.user + Settings.server.path_external
        file_name = 'compile' + Settings.project.name
        if not os.path.exists(fs.path_double_win(path_loc_win + "\\Build\\bin\\")):
            os.mkdir(path=fs.path_double_win(path_loc_win + "\\Build\\bin\\"))
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
            if Settings.server.compiler == 'gcc8':
                f.write("call make gcc8 -j7\n")
            else:
                f.write("call make -j7\n")
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

        result = winscp_path(file_name, Settings.local.path_winscp)
        # replace /script with /command
        os.remove(file_name)

        if result >= 1:
            print("error while executing code")
            print(result)

    elif Settings.device.system == 1:  # Intel Atom
        path_loc_win = Settings.project.path_local  # os.getcwd()
        path_dest_win = Settings.server.path_external
        file_name = 'compile' + Settings.project.name

        f = open(file_name, 'w+')
        f.write("option confirm off\n")
        f.write("open sftp://%s:%s@%s/ -hostkey=*\n" % (Settings.device.user, Settings.device.password, Settings.device.ip))
        if Settings.server.sync_files == '0':
            f.write("mkdir %s\n" % Settings.server.path_external)
            f.write("put -filemask=*|%s/Src/Windows/device/ %s %s//Src\n" % (path_loc_win, path_loc_win + "\\Src", path_dest_win))
        elif Settings.server.sync_files == '1':
            f.write("synchronize -filemask=*|%s/Src/Windows/device/ remote %s %s//Src\n" % (path_loc_win, path_loc_win + "\\Src", path_dest_win))
        f.write("cd " + Settings.server.path_external + "//Src\n")
        if not Settings.server.compile_mode:
            f.write("call make clean\n")
        if build == 'release':
            f.write("call make\n")
        elif build == 'debug':
            f.write("call make %s debug\n" % Settings.server.compiler)
        else:
            print("Error while exclude code, exiting.")
            return
        # TODO: Change hard-links to Settings parameter
        f.write("mv //root//navigation//bin//%s.bin //root//navigation//bin//%s.bin-backup\n")
        f.write("mv //root//%s//Build//bin//%s.bin\n" % (path_dest_win, Settings.project.name))
        f.write("exit\n")
        f.close()

        result = winscp_path(file_name, Settings.local.path_winscp)
        # replace /script with /command
        os.remove(file_name)

        if result >= 1:
            print("error while executing code")
            print(result)


def psplash_upload(Settings, self):
    """
    Upload psplash file with preset location to device (sFTP/SCP)

    :param Settings: configuration
    :param self: activity
    :return: None
    """
    file_name = fs.path_get_filename(Settings.project.path_psplash)
    path_dest = "//usr//bin//" + file_name
    script_file = 'psplash' + Settings.device.ip
    path_loc_win = Settings.project.path_psplash
    f = open(script_file, "w+")
    f.write("option confirm off\n")
    if Settings.device.file_protocol == 'sftp':
        f.write("open sftp://%s:%s@%s/ -hostkey=*\n" % (Settings.device.user, Settings.device.password, Settings.device.ip))
    elif Settings.device.file_protocol == 'scp':
        f.write("open scp://%s@%s:%s/ -hostkey=*\n" % (Settings.device.user, Settings.device.ip, Settings.device.password))
    f.write("put %s %s\n" % (path_loc_win, path_dest))
    f.write("chmod 777 %s\n" % path_dest)
    f.write("call ln -sfn %s psplash\n" % path_dest)
    f.write("exit\n")
    f.close()
    winscp_path(script_file, Settings.local.path_winscp)
    os.remove(script_file)
    self.setText("Psplash upload command has been sent.")
       

def clean(Settings):
    """
    Perform 'make clean' to sources on build-server (SFTP)

    :param Settings:
    :return: None
    """
    file_name = 'clean' + Settings.server.ip
    f = open(file_name, 'w+')
    f.write("option confirm off\n")
    f.write("open sftp://%s:%s@%s/ -hostkey=*\n" % (Settings.server.user, Settings.server.password, Settings.server.ip))
    f.write("cd //home//" + Settings.server.user + Settings.server.path_external + "//Src\n")
    f.write("call make clean\n")
    f.write("exit\n")
    f.close()

    result = winscp_path(file_name, Settings.local.path_winscp)
    # replace /script with /command
    os.remove(file_name)

    if result >= 1:
        print("error while executing code")
        print(result)
