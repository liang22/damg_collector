import argparse
import configparser
import datetime
import json
import locale
import logging
import os
import psutil
import subprocess
import sys
import time

_LOGGER_INST = None
_MANUAL_STAT = 0
_LOCALE_CODE = locale.getdefaultlocale()[1]


def handle_motion(motion_info):
    """
    Function to run the specified instruction.
    :param motion_info:             command information
    :return:                        none
    """
    locale_code = _LOCALE_CODE

    pip = subprocess.Popen(args=motion_info,
                           shell=True,
                           stdout=subprocess.PIPE,
                           stderr=subprocess.STDOUT)
    pip.wait()
    return_info = pip.stdout.read().decode(locale_code).strip()

    return return_info


class LoggerManage(object):
    """
    Class about functions to operate the log information.
    :method create_logger:
    """
    logger_home = 'C:\\dam' + 'g\\log\\'
    logger_name = 'collector.log'

    def create_logger(self):
        """
        Method to create a logger object.
        :return:
            log                     log instance
        """
        logger_path = self.logger_home + self.logger_name

        # Create the home path if it not exists.
        if not os.path.isdir(self.logger_home):
            os.makedirs(self.logger_home)

        # Create a new logger object.
        log = logging.getLogger('collector')
        log.setLevel(logging.DEBUG)

        # Setup the formatter of the logger object.
        logger_form = '%(asc' + 'time)s - %(level' + 'name)s - %(message)s'
        format_note = logging.Formatter(logger_form)

        # Setup the FileHandler of the logger object.
        logger_hand = logging.FileHandler(logger_path)
        logger_hand.setFormatter(format_note)
        log.addHandler(logger_hand)

        # Setup the global variable.
        global _LOGGER_INST
        _LOGGER_INST = log


class ScriptManage(object):
    """
    Class about functions to operate the shell scripts.
    :method create_script:
    """
    script_path = ''

    def __init__(self, script_path):
        """
        Method to build a script object.
        :param script_path:         script path
        """
        self.script_path = script_path

    def create_script(self, modify_info, record_path):
        """
        Method to modify the specified shell script.
        :param modify_info:         modify information
        :param record_path:         record file path
        :return:                    none
        """
        with open(file=self.script_path,
                  mode='a+') as fip:
            fip.writelines('set term' + 'out off;\n')
            fip.writelines('set echo off;\n')
            fip.writelines('set feedback off;\n')
            fip.writelines('set heading off;\n')
            fip.writelines('set pagesize 0;\n')
            fip.writelines('set lines 1024;\n')
            fip.writelines('spool '+record_path+';\n')
            fip.writelines(modify_info+'\n')
            fip.writelines('spool off;\n')
            fip.writelines('exit;\n')

        return None


class OracleManage(object):
    """
    Class about oracle operations.
    :method obtain_tps_total:
    :method obtain_qps_total:
    :method obtain_session:
    :method obtain_process:
    """
    handle_head = 'start /B sql' + 'plus / as sys' + 'dba'
    script_home = 'C:\\dam' + 'g\\tmp\\'

    def obtain_tps_total(self):
        """
        Method to get tps total number.
        :return:                    tps
        """
        script_name = 'show_tps.sql'
        record_name = 'show_tps.log'
        script_path = self.script_home + script_name
        record_path = self.script_home + record_name

        # Create and edit the shell script.
        shm = ScriptManage(script_path)

        # Make the instruction to get oracle information.
        modify_info = 'select sum(value) from v$sys' + 'stat where ' \
                      'name in (\'user commits\',\'user rollbacks\');'
        shm.create_script(modify_info=modify_info,
                          record_path=record_path)

        # Run the instruction to get oracle information.
        handle_path = '{head} @{path}'.\
            format(head=self.handle_head,
                   path=script_path)

        pip = subprocess.Popen(args=handle_path,
                               shell=True,
                               creationflags=subprocess.CREATE_NEW_CONSOLE)
        pip.wait()

        # Get the tps total
        while not os.path.exists(record_path):
            time.sleep(1)
        with open(record_path, 'r') as fip:
            return_info = fip.read().strip()

        # Delete the expire file.
        while True:
            try:
                if os.path.exists(script_path):
                    os.remove(script_path)
                if os.path.exists(record_path):
                    os.remove(record_path)
            except PermissionError:
                time.sleep(1)
            else:
                break

        return return_info

    def obtain_qps_total(self):
        """
        Method to get tps total number.
        :return:                    qps
        """
        script_name = 'show_qps.sql'
        record_name = 'show_qps.log'
        script_path = self.script_home + script_name
        record_path = self.script_home + record_name

        # Create and edit the shell script.
        shm = ScriptManage(script_path)

        # Make the instruction to get oracle information.
        modify_info = 'select value from v$sys' + 'stat where ' \
                      'name = \'execute count\';'
        shm.create_script(modify_info=modify_info,
                          record_path=record_path)

        # Run the instruction to get oracle information.
        handle_path = '{head} @{path}'.\
            format(head=self.handle_head,
                   path=script_path)

        pip = subprocess.Popen(args=handle_path,
                               shell=True,
                               creationflags=subprocess.CREATE_NEW_CONSOLE)
        pip.wait()

        # Get the tps total
        while not os.path.exists(record_path):
            time.sleep(1)
        with open(record_path, 'r') as fip:
            return_info = fip.read().strip()

        # Delete the expire file.
        while True:
            try:
                if os.path.exists(script_path):
                    os.remove(script_path)
                if os.path.exists(record_path):
                    os.remove(record_path)
            except PermissionError:
                time.sleep(1)
            else:
                break

        return return_info

    def obtain_session(self):
        """
        Method to get session number.
        :return:                    session number
        """
        script_name = 'show_session.sql'
        record_name = 'show_session.log'
        script_path = self.script_home + script_name
        record_path = self.script_home + record_name

        # Create and edit the shell script.
        shm = ScriptManage(script_path)

        # Make the instruction to get oracle information.
        modify_info = 'select count(1) from v$session' \
                      ' where status != \'INACTIVE\';'
        shm.create_script(modify_info=modify_info,
                          record_path=record_path)

        # Run the instruction to get oracle information.
        handle_path = '{head} @{path}'.\
            format(head=self.handle_head,
                   path=script_path)

        pip = subprocess.Popen(args=handle_path,
                               shell=True,
                               creationflags=subprocess.CREATE_NEW_CONSOLE)
        pip.wait()

        # Get the tps total
        while not os.path.exists(record_path):
            time.sleep(1)
        with open(record_path, 'r') as fip:
            return_info = fip.read().strip()

        # Delete the expire file.
        while True:
            try:
                if os.path.exists(script_path):
                    os.remove(script_path)
                if os.path.exists(record_path):
                    os.remove(record_path)
            except PermissionError:
                time.sleep(1)
            else:
                break

        return return_info

    def obtain_process(self):
        """
        Method to get tps total number.
        :return:                    qps
        """
        script_name = 'show_process.sql'
        record_name = 'show_process.log'
        script_path = self.script_home + script_name
        record_path = self.script_home + record_name

        # Create and edit the shell script.
        shm = ScriptManage(script_path)

        # Make the instruction to get oracle information.
        modify_info = 'select count(1) from v$process;'
        shm.create_script(modify_info=modify_info,
                          record_path=record_path)

        # Run the instruction to get oracle information.
        handle_path = '{head} @{path}'.\
            format(head=self.handle_head,
                   path=script_path)

        pip = subprocess.Popen(args=handle_path,
                               shell=True,
                               creationflags=subprocess.CREATE_NEW_CONSOLE)
        pip.wait()

        # Get the tps total
        while not os.path.exists(record_path):
            time.sleep(1)
        with open(record_path, 'r') as fip:
            return_info = fip.read().strip()

        # Delete the expire file.
        while True:
            try:
                if os.path.exists(script_path):
                    os.remove(script_path)
                if os.path.exists(record_path):
                    os.remove(record_path)
            except PermissionError:
                time.sleep(1)
            else:
                break

        return return_info


def handle_single():
    """
    Function to get and record the system & oracle information each 10s.
    :return:                    none
    """
    log = _LOGGER_INST
    count_num = 0
    script_home = 'C:\\dam' + 'g\\tmp'
    record_path = 'C:\\dam' + 'g\\log\\transit'
    resume_path = 'C:\\dam' + 'g\\log\\collect_stop'

    # Get option values from configuration.
    config_path = 'C:\\dam' + 'g\\etc\\dam' + 'g.conf'
    cfg = configparser.ConfigParser()
    cfg.read(config_path)

    try:
        limit_cpu = cfg.get("public", "limit_cpu")
    except Exception as e:
        log.debug(e)
        sys.exit(0)

    # Build tmp file home.
    if not os.path.exists(script_home):
        os.makedirs(script_home)

    # Get oracle information.
    ocm = OracleManage()
    try:
        tps_total = ocm.obtain_tps_total()
        qps_total = ocm.obtain_qps_total()
    except Exception as e:
        log.debug(e)
        sys.exit(0)

    while count_num != 6:
        # Get system information.
        # date_time = stm.obtain_date_time()
        cpu_usage = psutil.cpu_percent()
        if cpu_usage > int(limit_cpu):
            if not os.path.exists(resume_path):
                os.mkdir(resume_path)
            sys.exit(0)
        else:
            if os.path.exists(resume_path):
                os.rmdir(resume_path)

        mem_usage = psutil.virtual_memory().percent
        iop_total = psutil.disk_io_counters().read_count
        iop_total += psutil.disk_io_counters().write_count
        mbp_total = psutil.disk_io_counters().read_bytes
        mbp_total += psutil.disk_io_counters().write_bytes
        net_usage = psutil.net_io_counters().bytes_sent
        net_usage += psutil.net_io_counters().bytes_recv

        # Record the system & oracle information.
        record_info = '{cpu}|{mem}|{iop}|{mbp}|{net}|{tps}|{qps}|\n'\
            .format(cpu=cpu_usage,
                    mem=mem_usage,
                    iop=iop_total,
                    mbp=mbp_total,
                    net=net_usage,
                    tps=tps_total,
                    qps=qps_total)
        with open(record_path, 'a+') as fip:
            fip.writelines(record_info)

        count_num += 1
        time.sleep(9)

    return None


def handle_series():
    """
    Function to get and record the system & oracle information each 180s.
    :return:                    none
    """
    record_tran = 'C:\\dam' + 'g\\log\\transit'
    record_home = 'C:\\dam' + 'g\\data'
    record_norm = 'C:\\dam' + 'g\\data\\high_frequency.json'

    # Check if the server be busy.
    if os.path.exists('C:\\dam' + 'g\\log\\collect_stop'):
        sys.exit(0)
    else:
        time.sleep(1)

    # Build data file home.
    if not os.path.exists(record_home):
        os.makedirs(record_home)

    if not os.path.exists(record_tran):
        return None
    else:
        return_object = {}
        count = 0
        cpu = 0
        mem = 0
        iop = 0
        mbp = 0
        net = 0
        tps = 0
        qps = 0
        iop_start = 0
        mbp_start = 0
        net_start = 0
        tps_start = 0
        qps_start = 0

    # Get date time information.
    datetime_now = datetime.datetime.now()
    date_time = datetime_now.strftime('%Y%m%d%H%M%S')

    # Get recorded information.
    with open(record_tran, 'r') as fip:
        for inf in fip.readlines():
            if '||' in inf:
                continue
            else:
                count += 1

            cpu += float(inf.split('|')[0])
            mem += float(inf.split('|')[1])
            iop = int(inf.split('|')[2])
            mbp = int(inf.split('|')[3])
            net = int(inf.split('|')[4])
            tps = int(inf.split('|')[5])
            qps = int(inf.split('|')[6])

            if iop_start == 0:
                iop_start = int(inf.split('|')[2])
            if mbp_start == 0:
                mbp_start = int(inf.split('|')[3])
            if net_start == 0:
                net_start = int(inf.split('|')[4])
            if tps_start == 0:
                tps_start = int(inf.split('|')[5])
            if qps_start == 0:
                qps_start = int(inf.split('|')[6])

    if count == 0:
        sys.exit(0)

    cpu = str(round(cpu/count, 2))
    mem = str(round(mem/count, 2))
    iop = str(round((iop-iop_start)/10/count, 2))
    mbp = str(round((mbp-mbp_start)/10240/count, 2))
    net = str(round((net-net_start)/1048576/count, 2))
    tps = str(round((tps-tps_start)/10/count, 2))
    qps = str(round((qps-qps_start)/10/count, 2))

    # Record the system & oracle information.
    return_object.update({"time": date_time})
    return_object.update({"cpu": cpu})
    return_object.update({"mem": mem})
    return_object.update({"io"+"ps": iop})
    return_object.update({"mbps": mbp})
    return_object.update({"tps": tps})
    return_object.update({"qps": qps})
    return_object.update({"net": net})

    # Get session number & process number.
    ocm = OracleManage()
    session_num = ocm.obtain_session()
    process_num = ocm.obtain_process()
    return_object.update({"session": session_num})
    return_object.update({"process": process_num})

    # Write down the json information.
    if os.path.exists(record_norm):
        with open(record_norm, 'r') as fp:
            origin_info = json.load(fp)
    else:
        origin_info = []

    origin_info.append(return_object)
    object_json = json.dumps(origin_info)

    with open(record_norm, 'w') as fp:
        fp.write(object_json)

    # Delete the tmp information.
    os.remove(record_tran)

    return None


if __name__ == '__main__':
    # Make the module logger function.
    lgm = LoggerManage()
    lgm.create_logger()

    # Receive the values by actions and options.
    parser_args = argparse.ArgumentParser()
    action_args = parser_args.add_subparsers()
    action_args.required = True

    sin = action_args.add_parser('single')
    sin.set_defaults(func=handle_single)

    ser = action_args.add_parser('series')
    ser.set_defaults(func=handle_series)

    # Call the functions to deal with the specified action.
    # Print help information if the action not exists.
    arg = parser_args.parse_args()
    arg.func()
