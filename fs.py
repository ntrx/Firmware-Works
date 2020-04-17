# File operations functions
import os
import time


def cache_save(HISTORY_FILE, SETTING_VALUE):
    """
    Cache saving source history

    :param HISTORY_FILE: name of log file
    :type HISTORY_FILE: str
    :param SETTING_VALUE: line for saving
    :type SETTING_VALUE: str
    :return: None
    """
    # cache saving source history
    already_exist: bool = False

    if not os.path.isfile(HISTORY_FILE):
        f = open(HISTORY_FILE, "w")
        f.write("")
        f.close()

    with open(HISTORY_FILE, "r") as f:
        if SETTING_VALUE in f.read():
            already_exist = True
    f.close()

    if not already_exist:
        f = open(HISTORY_FILE, "a")
        f.write(SETTING_VALUE + "\n")
        f.close()


def cache_read(self, HISTORY_FILE):
    """
    Reading cache from history file

    :param self: object for saving history
    :param HISTORY_FILE: file name
    :type HISTORY_FILE: str
    :return: History has been writed to self
    """
    if os.path.isfile(HISTORY_FILE):
        self.clear()
        index: int = 0
        with open(HISTORY_FILE, "r") as f:
            while True:
                line = f.readline()
                if not line:
                    break
                self.addItem(line)
                index += 1
        self.setCurrentIndex(index)
        f.close()


def cache_create(file_list):
    """
    Creation cache files (if not found before)

    :param file_list: list of files which need to create
    :return: None
    """
    for file in file_list:
        if not os.path.isfile(file):
            f = open(file, "w")
            f.write("")
            f.close()


def path_double_win(path):
    """
    Redirect slashes in string for Windows

    :param path: PATH string without doubled slashes
    :type path: str
    :return: new string
    """
    if os.name == "nt":
        result = ""
        for symbol in range(0, len(path)):
            if path[symbol] == '/':
                result += '\\'
                continue
            result += path[symbol]
        print("PATH: %s => %s" % (path, result))
    else:
        pass
    return result


def path_double_nix(path):
    """
    Doubles slashes in string for Linux

    :param path: PATH string without doubled slashes
    :type path: str
    :return: new string
    """
    result = ""
    for symbol in range(0, len(path)):
        if path[symbol] == '/':
            result += '//'
            continue
        result += path[symbol]
    return result


def path_get_filename(path):
    """
    Getting filename in PATH string

    :param path: PATH string with doubled slashes and file name at end
    :type path: str
    :return: only file name
    """
    result = ""
    reversed_path = ""
    reversed_result = ""
    for symbol in reversed(range(len(path))):
        reversed_path += path[symbol]
    for symbol in range(0, len(reversed_path)):
        if reversed_path[symbol] == '\\':
            break
        result += reversed_path[symbol]
    for symbol in reversed(range(len(result))):
        reversed_result += result[symbol]
    return reversed_result


def path_get_firmware(path, self):
    """
    Getting size and time creation of file (specified for firmwares)

    :param path: PATH to firmware
    :type path: str
    :param self: activity
    :return: Text to self about firmware status
    """
    firmware_path = path
    if os.path.exists(firmware_path):
        firmware_size = os.path.getsize(firmware_path)
        firmware_time = os.path.getctime(firmware_path)
        self.setText("Firmware compiled at %s, size: %2.2f MB" % (time.ctime(firmware_time), firmware_size / 1024000))
    else:
        self.setText("No firmware compiled found.")


def path_quotes_check(path):
    """
    Take path with spaced catalogs with qoutes

    :param path: path
    :type path: str
    :return: New path, with quoted catalogs with space in name
    """
    space_position = path.find(" ")
    last_slash = 0
    first_slash = 0
    if space_position >= 0:
        for i in range(space_position, len(path)):
            if path[i] == '\\':
                last_slash = i
                break
        for i in range(0, space_position):
            if path[i] == '\\':
                first_slash = i+1
                break
        new_path = path[0:first_slash]
        new_path += "\""
        new_path += path[first_slash:last_slash]
        new_path += "\""
        new_path += path[last_slash:len(path)]
        print("PATH: %s => %s" % (path, new_path))
        return new_path
    else:
        return path
