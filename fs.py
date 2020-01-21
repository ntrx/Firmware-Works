# File operations functions
import os
import time


def cache_save(HISTORY_FILE, SETTING_VALUE):
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
    if os.path.isfile(HISTORY_FILE):
        self.clear()
        with open(HISTORY_FILE, "r") as f:
            while True:
                line = f.readline()
                if not line:
                    break
                self.addItem(line)
        f.close()


def cache_create(file_list):
    for file in file_list:
        if not os.path.isfile(file):
            f = open(file, "w")
            f.write("")
            f.close()


def path_double_win(path):
    """
    :param path: PATH string without doubled slashes
    :type path: str
    :return:
    """
    result = ""
    for symbol in range(0, len(path)):
        if path[symbol] == '/':
            result += '\\'
            continue
        result += path[symbol]
    return result


def path_double_nix(path):
    """
    :param path: PATH string without doubled slashes
    :type path: str
    :return:
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
    firmware_path = path
    if os.path.exists(firmware_path):
        firmware_size = os.path.getsize(firmware_path)
        firmware_time = os.path.getctime(firmware_path)
        self.setText("Firmware compiled at %s, size: %2.2f MB" % (time.ctime(firmware_time), firmware_size / 1024000))
    else:
        self.setText("No firmware compiled found.")
