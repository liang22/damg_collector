#!/opt/python3/bin/python3
# -*- coding:utf-8 -*-

import configparser
import os
import sys
import time


# Function to do something.
def run_daemon():
    time.sleep(600)
    while True:
        # Check collector's log status.
        cfg = configparser.ConfigParser()
        cfg.read('/etc/dam' + 'g.conf')

        try:
            config_stat = cfg.get('process', 'finish')
        except configparser.NoSectionError:
            config_stat = '1'
        except configparser.NoOptionError:
            config_stat = '1'

        # Check collector's real status.
        check_cmd = 'cat /etc/cron' \
                    'tab |grep dam_high >/dev/null 2>&1'
        system_stat = os.system(check_cmd)

        # If collector quit without 'finish' action,
        # Start the collector again.
        if config_stat != '0' and system_stat != 0:
            enable_demo = 'dam_collect start >/dev/null 2>&1'
            os.system(enable_demo)
        elif config_stat == '0' and system_stat == 0:
            disable_demo = 'dam_collect finish >/dev/null 2>&1'
            os.system(disable_demo)            

        time.sleep(600)


# Function to create the daemon.
def create_daemon():
    # create - fork 1
    try:
        if os.fork() > 0:
            sys.exit(0)
    except OSError as e:
        print(e)
        sys.exit(1)

    # it separates the son from the father
    os.chdir('/')
    os.setsid()
    os.umask(0)

    # create - fork 2
    try:
        pid = os.fork()
        if pid > 0:
            print('Daemon PID ' + str(pid))
            sys.exit(0)
    except OSError as e:
        print(e)
        sys.exit(1)
 
    run_daemon()


if __name__ == '__main__':
    create_daemon()
