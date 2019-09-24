# File operations functions
import os


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
