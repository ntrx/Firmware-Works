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