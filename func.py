#!/usr/bin/env python
# list of functions for scripts
import os
import subprocess

from core import _SCP_
from core import _SFTP_


def is_online(host, times=1):
    """
    Ping specified IP address (once)

    :param host: ip address
    :type host: str
    :param times: how many times to do ping
    :type times: int
    :return: 1 - online, 0 - offline
    """
    if os.name == 'nt':
        ping_status = subprocess.call("ping -n %d %s" % (times, host))
        if ping_status == 0:  # active
            return 1
        elif ping_status == 0:
            return 0
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


def get_value(line, start):
    """
    Getting parameter value from string. Begin from 'start'

    :param line: line with parameter value
    :type line: str
    :param start: first byte
    :type start: int
    :return: value of parameter
    """
    value = ""
    for i in range(start, len(line)):
        if line[i] == " " and line[i+1] == "'":
            j = i+2
            while line[j] != "'":
                value += line[j]
                j += 1
    return value


def check_value(line):
    """
    Clearing new line symbol from str

    :param line: input string
    :type line: str
    :return: cleared string
    """
    new_value = ""
    for i in range(0, len(line)):
        if line[i] != '\n':
            new_value += line[i]
    return new_value


def protocol_get(self):
    """
    Returning selected protocol (str) in combobox

    :param self:
    :return: selected protocol
    """
    if self.comboBox_8.currentText() == 'SCP':
        return _SCP_
    elif self.comboBox_8.currentText() == 'SFTP':
        return _SFTP_


def prompt_print(data):
    """
    Display data to console from output result after exec_command

    :param data:
    :return: display
    """
    i = 0
    while i < len(data):
        print(chr(data[i]), end="")
        i += 1
