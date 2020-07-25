import configparser
import json
import locale
import logging
import os
import psutil
import subprocess
import time

_LOGGER_INST = None
_MANUAL_STAT = 'yes'
_COLLECT_MAX = 0
_COLLECT_NUM = 0
_LOCALE_CODE = locale.getdefaultlocale()[1]


def record_degree():
    """
    Function to record max/current collect object number.
    :return:
    """
    config_path = 'C:\\dam' + 'g\\etc\\dam' + 'g.conf'

    # Read the configuration.
    cfg = configparser.ConfigParser()
    cfg.read(config_path)

    try:
        degree_count = int(cfg.get('process', 'degree_count'))
        degree_total = int(cfg.get('process', 'degree_total'))
    except configparser.NoSectionError:
        cfg.add_section('process')
        degree_count = 0
        degree_total = 0
    except configparser.NoOptionError:
        degree_count = 0
        degree_total = 0

    # Setup the process option.
    degree_count += _COLLECT_NUM
    degree_total += _COLLECT_MAX

    cfg.set('process', 'degree_count', str(degree_count))
    cfg.set('process', 'degree_total', str(degree_total))
    cfg.write(open(config_path, "w+"))

    return None


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
    """
    oracle_user = ''
    oracle_home = ''
    handle_head = 'start /B sql' + 'plus / as sys' + 'dba'
    logger_inst = None

    def __init__(self, oracle_user, oracle_home):
        self.oracle_user = oracle_user
        self.oracle_home = oracle_home
        self.logger_inst = _LOGGER_INST

    def obtain_object_type(self):
        """
        Method to get object type.
        :return:                    object types
        """
        log = self.logger_inst

        global _COLLECT_MAX
        global _COLLECT_NUM
        _COLLECT_MAX += 1

        # Make the shell script path.
        script_name = 'list_obj_type.sql'
        record_name = 'list_obj_type.log'
        script_path = self.oracle_home + script_name
        record_path = self.oracle_home + record_name

        # Create and edit the shell script.
        modify_info = 'select object_type from dba_objects' \
                      ' where owner=\'{user}\' group by object_type;'\
            .format(user=self.oracle_user)
        log.debug(modify_info)

        shm = ScriptManage(script_path)
        shm.create_script(modify_info=modify_info,
                          record_path=record_path)

        # Run the shell script by oracle user.
        handle_path = '{head} @{path}'.\
            format(head=self.handle_head,
                   path=script_path)

        pip = subprocess.Popen(args=handle_path,
                               shell=True,
                               creationflags=subprocess.CREATE_NEW_CONSOLE)
        pip.wait()

        while not os.path.exists(record_path):
            time.sleep(1)

        # Get the oracle information.
        with open(record_path, 'r') as fip:
            return_info = fip.readlines()

        # Delete the expire file.
        if return_info:
            _COLLECT_NUM += 1

            while True:
                try:
                    if os.path.exists(script_path):
                        os.remove(script_path)
                    if os.path.exists(record_path):
                        os.remove(record_path)
                except Exception as e:
                    log.debug(e)
                    time.sleep(1)
                else:
                    break

        return return_info

    def obtain_object_name(self, object_type):
        """
        Method to get object list.
        :param object_type:         object type
        :return:                    object name list
        """
        log = self.logger_inst

        global _COLLECT_MAX
        global _COLLECT_NUM
        _COLLECT_MAX += 1

        # Make the shell script path.
        script_name = 'list_obj_name.sql'
        record_name = 'list_obj_name.log'
        script_path = self.oracle_home + script_name
        record_path = self.oracle_home + record_name

        # Create and edit the shell script.
        shm = ScriptManage(script_path)

        modify_info = 'select object_name from dba_objects where' \
                      ' owner=\'{user}\' and object_type=\'{type}\';'\
            .format(user=self.oracle_user,
                    type=object_type)
        log.debug(modify_info)

        shm.create_script(modify_info=modify_info,
                          record_path=record_path)

        # Run the shell script by oracle user.
        handle_path = '{head} @{path}'.\
            format(head=self.handle_head,
                   path=script_path)

        pip = subprocess.Popen(args=handle_path,
                               shell=True,
                               creationflags=subprocess.CREATE_NEW_CONSOLE)
        pip.wait()

        while not os.path.exists(record_path):
            time.sleep(1)

        # Get the oracle information.
        with open(record_path, 'r') as fip:
            return_info = fip.readlines()

        # Delete the expire file.
        if return_info:
            _COLLECT_NUM += 1

            while True:
                try:
                    if os.path.exists(script_path):
                        os.remove(script_path)
                    if os.path.exists(record_path):
                        os.remove(record_path)
                except Exception as e:
                    log.debug(e)
                    time.sleep(1)
                else:
                    break

        return return_info

    def obtain_object_size(self):
        """
        Method to get object size(table, index, lob).
        :return:                    size
        """
        log = self.logger_inst

        global _COLLECT_MAX
        global _COLLECT_NUM
        _COLLECT_MAX += 1

        # Make the shell script path.
        script_name = 'list_obj_size.sql'
        record_name = 'list_obj_size.log'
        script_path = self.oracle_home + script_name
        record_path = self.oracle_home + record_name

        # Create and edit the shell script.
        shm = ScriptManage(script_path)

        modify_info = 'select segment_type||\'|\'||sum(bytes)' \
                      ' from dba_segments where segment_type in' \
                      ' (\'TABLE\', \'INDEX\', \'LOB' \
                      'SEGMENT\') and owner = \''
        modify_info += self.oracle_user + '\' group by segment_type;'
        log.debug(modify_info)

        shm.create_script(modify_info=modify_info,
                          record_path=record_path)

        # Run the shell script by oracle user.
        handle_path = '{head} @{path}'.\
            format(head=self.handle_head,
                   path=script_path)

        pip = subprocess.Popen(args=handle_path,
                               shell=True,
                               creationflags=subprocess.CREATE_NEW_CONSOLE)
        pip.wait()

        while not os.path.exists(record_path):
            time.sleep(1)

        # Get the oracle information.
        with open(record_path, 'r') as fip:
            return_info = fip.readlines()

        # Delete the expire file.
        if return_info:
            _COLLECT_NUM += 1

            while True:
                try:
                    if os.path.exists(script_path):
                        os.remove(script_path)
                    if os.path.exists(record_path):
                        os.remove(record_path)
                except Exception as e:
                    log.debug(e)
                    time.sleep(1)
                else:
                    break

        return return_info

    def obtain_object_link(self):
        """
        Method to get object link information.
        :return:                    link information
        """
        log = self.logger_inst

        global _COLLECT_MAX
        global _COLLECT_NUM
        _COLLECT_MAX += 1

        # Make the shell script path.
        script_name = 'list_obj_link.sql'
        record_name = 'list_obj_link.log'
        script_path = self.oracle_home + script_name
        record_path = self.oracle_home + record_name

        # Create and edit the shell script.
        shm = ScriptManage(script_path)

        modify_info = 'select username||\'|\'||db_link||\'|\'||host' \
                      ' from dba_db_links where owner=\'{user}\';'\
            .format(user=self.oracle_user)
        log.debug(modify_info)

        shm.create_script(modify_info=modify_info,
                          record_path=record_path)

        # Run the shell script by oracle user.
        handle_path = '{head} @{path}'.\
            format(head=self.handle_head,
                   path=script_path)

        pip = subprocess.Popen(args=handle_path,
                               shell=True,
                               creationflags=subprocess.CREATE_NEW_CONSOLE)
        pip.wait()

        while not os.path.exists(record_path):
            time.sleep(1)

        # Get the oracle information.
        with open(record_path, 'r') as fip:
            return_info = fip.readlines()

        # Delete the expire file.
        if return_info:
            _COLLECT_NUM += 1

            while True:
                try:
                    if os.path.exists(script_path):
                        os.remove(script_path)
                    if os.path.exists(record_path):
                        os.remove(record_path)
                except Exception as e:
                    log.debug(e)
                    time.sleep(1)
                else:
                    break

        return return_info

    def obtain_version(self):
        """
        Method to get oracle version.
        :return:                    version
        """
        log = self.logger_inst

        global _COLLECT_MAX
        global _COLLECT_NUM
        _COLLECT_MAX += 1

        # Make the shell script path.
        script_name = 'show_ver.sql'
        record_name = 'show_ver.log'
        script_path = self.oracle_home + script_name
        record_path = self.oracle_home + record_name

        # Create and edit the shell script.
        # where SUB STR(PRODUCT,1,6)='Oracle'
        shm = ScriptManage(script_path)

        modify_info = 'select version from product_component_version' \
                      ' where product like \'Oracle%\';'
        log.debug(modify_info)

        shm.create_script(modify_info=modify_info,
                          record_path=record_path)

        # Run the shell script by oracle user.
        handle_path = '{head} @{path}'.\
            format(head=self.handle_head,
                   path=script_path)

        pip = subprocess.Popen(args=handle_path,
                               shell=True,
                               creationflags=subprocess.CREATE_NEW_CONSOLE)
        pip.wait()

        while not os.path.exists(record_path):
            time.sleep(1)

        # Get the oracle information.
        with open(record_path, 'r') as fip:
            return_info = fip.readline().strip()

        # Delete the expire file.
        if return_info:
            _COLLECT_NUM += 1

            while True:
                try:
                    if os.path.exists(script_path):
                        os.remove(script_path)
                    if os.path.exists(record_path):
                        os.remove(record_path)
                except Exception as e:
                    log.debug(e)
                    time.sleep(1)
                else:
                    break

        return return_info

    def obtain_database(self):
        """
        Method to get database information.
        :return:                    database information
        """
        log = self.logger_inst

        global _COLLECT_MAX
        global _COLLECT_NUM
        _COLLECT_MAX += 1

        # Make the shell script path.
        script_name = 'show_dbs.sql'
        record_name = 'show_dbs.log'
        script_path = self.oracle_home + script_name
        record_path = self.oracle_home + record_name

        # Create and edit the shell script.
        modify_info = 'select db' \
                      'id||\'|\'||name||\'|\'||log_mode' \
                      ' from v$database;'
        log.debug(modify_info)

        shm = ScriptManage(script_path)
        shm.create_script(modify_info=modify_info,
                          record_path=record_path)

        # Run the shell script by oracle user.
        handle_path = '{head} @{path}'.\
            format(head=self.handle_head,
                   path=script_path)

        pip = subprocess.Popen(args=handle_path,
                               shell=True,
                               creationflags=subprocess.CREATE_NEW_CONSOLE)
        pip.wait()

        while not os.path.exists(record_path):
            time.sleep(1)

        # Get the oracle information.
        with open(record_path, 'r') as fip:
            return_info = fip.readline().strip()

        # Delete the expire file.
        if return_info:
            _COLLECT_NUM += 1

            while True:
                try:
                    if os.path.exists(script_path):
                        os.remove(script_path)
                    if os.path.exists(record_path):
                        os.remove(record_path)
                except Exception as e:
                    log.debug(e)
                    time.sleep(1)
                else:
                    break

        return return_info

    def obtain_sga_size(self):
        """
        Method to get sga size.
        :return:                    sga size
        """
        log = self.logger_inst

        global _COLLECT_MAX
        global _COLLECT_NUM
        _COLLECT_MAX += 1

        # Make the shell script path.
        script_name = 'show_sga.sql'
        record_name = 'show_sga.log'
        script_path = self.oracle_home + script_name
        record_path = self.oracle_home + record_name

        # Create and edit the shell script.
        shm = ScriptManage(script_path)

        modify_info = 'select round(sum(value)/1024/1024/1024) from v$sga;'
        log.debug(modify_info)

        shm.create_script(modify_info=modify_info,
                          record_path=record_path)

        # Run the shell script by oracle user.
        handle_path = '{head} @{path}'.\
            format(head=self.handle_head,
                   path=script_path)

        pip = subprocess.Popen(args=handle_path,
                               shell=True,
                               creationflags=subprocess.CREATE_NEW_CONSOLE)
        pip.wait()

        while not os.path.exists(record_path):
            time.sleep(1)

        # Get the oracle information.
        with open(record_path, 'r') as fip:
            return_info = fip.readline().strip()

        # Delete the expire file.
        if return_info:
            _COLLECT_NUM += 1

            while True:
                try:
                    if os.path.exists(script_path):
                        os.remove(script_path)
                    if os.path.exists(record_path):
                        os.remove(record_path)
                except Exception as e:
                    log.debug(e)
                    time.sleep(1)
                else:
                    break

        return return_info

    def obtain_pga_size(self):
        """
        Method to get pga size.
        :return:                    pga size
        """
        log = self.logger_inst

        global _COLLECT_MAX
        global _COLLECT_NUM
        _COLLECT_MAX += 1

        # Make the shell script path.
        script_name = 'show_pga.sql'
        record_name = 'show_pga.log'
        script_path = self.oracle_home + script_name
        record_path = self.oracle_home + record_name

        # Create and edit the shell script.
        shm = ScriptManage(script_path)

        modify_info = 'select round(value/1024/1024/1024) from v$pga' \
                      'stat where name=\'aggregate PGA target parameter\';'
        log.debug(modify_info)

        shm.create_script(modify_info=modify_info,
                          record_path=record_path)

        # Run the shell script by oracle user.
        handle_path = '{head} @{path}'.\
            format(head=self.handle_head,
                   path=script_path)

        pip = subprocess.Popen(args=handle_path,
                               shell=True,
                               creationflags=subprocess.CREATE_NEW_CONSOLE)
        pip.wait()

        while not os.path.exists(record_path):
            time.sleep(1)

        # Get the oracle information.
        with open(record_path, 'r') as fip:
            return_info = fip.readline().strip()

        # Delete the expire file.
        if return_info:
            _COLLECT_NUM += 1

            while True:
                try:
                    if os.path.exists(script_path):
                        os.remove(script_path)
                    if os.path.exists(record_path):
                        os.remove(record_path)
                except Exception as e:
                    log.debug(e)
                    time.sleep(1)
                else:
                    break

        return return_info

    def obtain_view_num(self):
        """
        Method to get materialized view object number.
        :return:                    object number
        """
        log = self.logger_inst

        global _COLLECT_MAX
        global _COLLECT_NUM
        _COLLECT_MAX += 1

        # Make the shell script path.
        script_name = 'show_mat.sql'
        record_name = 'show_mat.log'
        script_path = self.oracle_home + script_name
        record_path = self.oracle_home + record_name

        # Create and edit the shell script.
        shm = ScriptManage(script_path)

        modify_info = 'select count(1) from dba_m' \
                      'views where owner=\'{user}\';'\
            .format(user=self.oracle_user)
        log.debug(modify_info)

        shm.create_script(modify_info=modify_info,
                          record_path=record_path)

        # Run the shell script by oracle user.
        handle_path = '{head} @{path}'.\
            format(head=self.handle_head,
                   path=script_path)

        pip = subprocess.Popen(args=handle_path,
                               shell=True,
                               creationflags=subprocess.CREATE_NEW_CONSOLE)
        pip.wait()

        while not os.path.exists(record_path):
            time.sleep(1)

        # Get the oracle information.
        with open(record_path, 'r') as fip:
            return_info = fip.readline().strip()

        # Delete the expire file.
        if return_info:
            _COLLECT_NUM += 1

            while True:
                try:
                    if os.path.exists(script_path):
                        os.remove(script_path)
                    if os.path.exists(record_path):
                        os.remove(record_path)
                except Exception as e:
                    log.debug(e)
                    time.sleep(1)
                else:
                    break

        return return_info

    def obtain_tran_num(self):
        """
        Method to get Transaction object number.
        :return:                    object number
        """
        log = self.logger_inst

        global _COLLECT_MAX
        global _COLLECT_NUM
        _COLLECT_MAX += 1

        # Make the shell script path.
        script_name = 'show_tra.sql'
        record_name = 'show_tra.log'
        script_path = self.oracle_home + script_name
        record_path = self.oracle_home + record_name

        # Create and edit the shell script.
        shm = ScriptManage(script_path)

        modify_info = 'select count(1) from v$transaction;'
        log.debug(modify_info)

        shm.create_script(modify_info=modify_info,
                          record_path=record_path)

        # Run the shell script by oracle user.
        handle_path = '{head} @{path}'.\
            format(head=self.handle_head,
                   path=script_path)

        pip = subprocess.Popen(args=handle_path,
                               shell=True,
                               creationflags=subprocess.CREATE_NEW_CONSOLE)
        pip.wait()

        while not os.path.exists(record_path):
            time.sleep(1)

        # Get the oracle information.
        with open(record_path, 'r') as fip:
            return_info = fip.readline().strip()

        # Delete the expire file.
        if return_info:
            _COLLECT_NUM += 1

            while True:
                try:
                    if os.path.exists(script_path):
                        os.remove(script_path)
                    if os.path.exists(record_path):
                        os.remove(record_path)
                except Exception as e:
                    log.debug(e)
                    time.sleep(1)
                else:
                    break

        return return_info

    def obtain_oracle_size(self):
        """
        Method to get oracle size.
        :return:                    oracle size
        """
        log = self.logger_inst

        global _COLLECT_MAX
        global _COLLECT_NUM
        _COLLECT_MAX += 1

        # Make the shell script path.
        script_name = 'show_ocr_size.sql'
        record_name = 'show_ocr_size.log'
        script_path = self.oracle_home + script_name
        record_path = self.oracle_home + record_name

        # Create and edit the shell script.
        shm = ScriptManage(script_path)

        modify_info = 'select round(sum(bytes)/1024/1048576, 2) GB' \
                      ' from (select sum(BYTES) as BYTES FROM Dba_Data_Files' \
                      ' union select bytes from dba_temp_files' \
                      ' union select sum(bytes) bytes from v$log);'
        log.debug(modify_info)

        shm.create_script(modify_info=modify_info,
                          record_path=record_path)

        # Run the shell script by oracle user.
        handle_path = '{head} @{path}'.\
            format(head=self.handle_head,
                   path=script_path)

        pip = subprocess.Popen(args=handle_path,
                               shell=True,
                               creationflags=subprocess.CREATE_NEW_CONSOLE)
        pip.wait()

        while not os.path.exists(record_path):
            time.sleep(1)

        # Get the oracle information.
        with open(record_path, 'r') as fip:
            return_info = fip.readline().strip()

        # Delete the expire file.
        if return_info:
            _COLLECT_NUM += 1

            while True:
                try:
                    if os.path.exists(script_path):
                        os.remove(script_path)
                    if os.path.exists(record_path):
                        os.remove(record_path)
                except Exception as e:
                    log.debug(e)
                    time.sleep(1)
                else:
                    break

        return return_info

    def obtain_data_size(self):
        """
        Method to get data size.
        :return:                    data size
        """
        log = self.logger_inst

        global _COLLECT_MAX
        global _COLLECT_NUM
        _COLLECT_MAX += 1

        # Make the shell script path.
        script_name = 'show_ocr_used.sql'
        record_name = 'show_ocr_used.log'
        script_path = self.oracle_home + script_name
        record_path = self.oracle_home + record_name

        # Create and edit the shell script.
        shm = ScriptManage(script_path)

        modify_info = 'select round(sum(bytes)/1024/1024/1024,2)' \
                      ' from (select bytes_used as BYTES' \
                      ' from GV_$TEMP_SPACE_HEADER union' \
                      ' select sum(BYTES) as BYTES' \
                      ' from dba_segments union' \
                      ' select sum(bytes) bytes from v$log);'
        log.debug(modify_info)

        shm.create_script(modify_info=modify_info,
                          record_path=record_path)

        # Run the shell script by oracle user.
        handle_path = '{head} @{path}'.\
            format(head=self.handle_head,
                   path=script_path)

        pip = subprocess.Popen(args=handle_path,
                               shell=True,
                               creationflags=subprocess.CREATE_NEW_CONSOLE)
        pip.wait()
        time.sleep(2)

        while not os.path.exists(record_path):
            time.sleep(1)

        # Get the oracle information.
        with open(record_path, 'r') as fip:
            return_info = fip.readline().strip()

        # Delete the expire file.
        if return_info:
            _COLLECT_NUM += 1

            while True:
                try:
                    if os.path.exists(script_path):
                        os.remove(script_path)
                    if os.path.exists(record_path):
                        os.remove(record_path)
                except Exception as e:
                    log.debug(e)
                    time.sleep(1)
                else:
                    break

        return return_info

    def obtain_db_files(self):
        """
        Method to get db files.
        :return:                    db files
        """
        log = self.logger_inst

        global _COLLECT_MAX
        global _COLLECT_NUM
        _COLLECT_MAX += 1

        # Make the shell script path.
        script_name = 'show_db_file.sql'
        record_name = 'show_db_file.log'
        script_path = self.oracle_home + script_name
        record_path = self.oracle_home + record_name

        # Create and edit the shell script.
        shm = ScriptManage(script_path)

        modify_info = 'select (select count(1) as count from dba_data_files)' \
                      ' + (select count(1) as count from dba_temp_files)' \
                      ' + (select count(1) as count from v$logfile)' \
                      ' DB_FILES from dual;'
        log.debug(modify_info)

        shm.create_script(modify_info=modify_info,
                          record_path=record_path)

        # Run the shell script by oracle user.
        handle_path = '{head} @{path}'.\
            format(head=self.handle_head,
                   path=script_path)

        pip = subprocess.Popen(args=handle_path,
                               shell=True,
                               creationflags=subprocess.CREATE_NEW_CONSOLE)
        pip.wait()

        while not os.path.exists(record_path):
            time.sleep(1)

        # Get the oracle information.
        with open(record_path, 'r') as fip:
            return_info = fip.readline().strip()

        # Delete the expire file.
        if return_info:
            _COLLECT_NUM += 1

            while True:
                try:
                    if os.path.exists(script_path):
                        os.remove(script_path)
                    if os.path.exists(record_path):
                        os.remove(record_path)
                except Exception as e:
                    log.debug(e)
                    time.sleep(1)
                else:
                    break

        return return_info

    def obtain_segment_num(self):
        """
        Method to get segment number.
        :return:                    segment number
        """
        log = self.logger_inst

        global _COLLECT_MAX
        global _COLLECT_NUM
        _COLLECT_MAX += 1

        # Make the shell script path.
        script_name = 'show_seg_num.sql'
        record_name = 'show_seg_num.log'
        script_path = self.oracle_home + script_name
        record_path = self.oracle_home + record_name

        # Create and edit the shell script.
        shm = ScriptManage(script_path)

        modify_info = 'select count(1) from dba_segments' \
                      ' where owner=\'{user}\';'\
            .format(user=self.oracle_user)
        log.debug(modify_info)

        shm.create_script(modify_info=modify_info,
                          record_path=record_path)

        # Run the shell script by oracle user.
        handle_path = '{head} @{path}'.\
            format(head=self.handle_head,
                   path=script_path)

        pip = subprocess.Popen(args=handle_path,
                               shell=True,
                               creationflags=subprocess.CREATE_NEW_CONSOLE)
        pip.wait()

        while not os.path.exists(record_path):
            time.sleep(1)

        # Get the oracle information.
        with open(record_path, 'r') as fip:
            return_info = fip.readline().strip()

        # Delete the expire file.
        if return_info:
            _COLLECT_NUM += 1

            while True:
                try:
                    if os.path.exists(script_path):
                        os.remove(script_path)
                    if os.path.exists(record_path):
                        os.remove(record_path)
                except Exception as e:
                    log.debug(e)
                    time.sleep(1)
                else:
                    break

        return return_info

    def obtain_obj_type_num(self):
        """
        Method to get object type number.
        :return:                    type number
        """
        log = self.logger_inst

        global _COLLECT_MAX
        global _COLLECT_NUM
        _COLLECT_MAX += 1

        # Make the shell script path.
        script_name = 'show_obj_typ_num.sql'
        record_name = 'show_obj_typ_num.log'
        script_path = self.oracle_home + script_name
        record_path = self.oracle_home + record_name

        # Create and edit the shell script.
        shm = ScriptManage(script_path)

        modify_info = 'select count(distinct object_type)' \
                      ' from dba_objects where owner=\'{user}\';'\
            .format(user=self.oracle_user)
        log.debug(modify_info)

        shm.create_script(modify_info=modify_info,
                          record_path=record_path)

        # Run the shell script by oracle user.
        handle_path = '{head} @{path}'.\
            format(head=self.handle_head,
                   path=script_path)

        pip = subprocess.Popen(args=handle_path,
                               shell=True,
                               creationflags=subprocess.CREATE_NEW_CONSOLE)
        pip.wait()

        while not os.path.exists(record_path):
            time.sleep(1)

        # Get the oracle information.
        with open(record_path, 'r') as fip:
            return_info = fip.readline().strip()

        # Delete the expire file.
        if return_info:
            _COLLECT_NUM += 1

            while True:
                try:
                    if os.path.exists(script_path):
                        os.remove(script_path)
                    if os.path.exists(record_path):
                        os.remove(record_path)
                except Exception as e:
                    log.debug(e)
                    time.sleep(1)
                else:
                    break

        return return_info

    def obtain_wait_event(self):
        """
        Method to get wait event.
        :return:                    process number
        """
        log = self.logger_inst

        global _COLLECT_MAX
        global _COLLECT_NUM
        _COLLECT_MAX += 1

        # Make the shell script path.
        script_name = 'show_wait_event.sql'
        record_name = 'show_wait_event.log'
        script_path = self.oracle_home + script_name
        record_path = self.oracle_home + record_name

        # Create and edit the shell script.
        shm = ScriptManage(script_path)

        modify_info = 'select event||\'|\'||total_waits||\'|\'||' \
                      'avg_waits||\'|\'||wait_class as wait_event ' \
                      'from (select event, round(sum(total_waits) / 100) ' \
                      'total_waits, trunc(avg(time_waited / 100), 2) ' \
                      'as avg_waits, wait_class from v$session_event ' \
                      'where wait_class != \'Idle\' group by event, ' \
                      'wait_class order by total_waits desc) where row' \
                      'num < 11;'
        log.debug(modify_info)
        shm.create_script(modify_info=modify_info,
                          record_path=record_path)

        # Run the shell script by oracle user.
        handle_path = '{head} @{path}'.\
            format(head=self.handle_head,
                   path=script_path)

        pip = subprocess.Popen(args=handle_path,
                               shell=True,
                               creationflags=subprocess.CREATE_NEW_CONSOLE)
        pip.wait()

        while not os.path.exists(record_path):
            time.sleep(1)

        # Get the oracle information.
        with open(record_path, 'r') as fip:
            return_info = fip.readlines()

        # Delete the expire file.
        if return_info:
            _COLLECT_NUM += 1

            while True:
                try:
                    if os.path.exists(script_path):
                        os.remove(script_path)
                    if os.path.exists(record_path):
                        os.remove(record_path)
                except Exception as e:
                    log.debug(e)
                    time.sleep(1)
                else:
                    break

        return return_info

    def obtain_health(self):
        """
        Method to get oracle health.
        :return:                    oracle health
        """
        log = self.logger_inst

        global _COLLECT_MAX
        global _COLLECT_NUM
        _COLLECT_MAX += 1
        _COLLECT_NUM += 1

        # Make the shell script path.
        script_name = 'show_inst_name.sql'
        record_name = 'show_inst_name.log'
        script_path = self.oracle_home + script_name
        record_path = self.oracle_home + record_name

        # Create and edit the shell script.
        shm = ScriptManage(script_path)

        modify_info = 'select value from v$parameter' \
                      ' where name =\'instance_name\';'
        log.debug(modify_info)
        shm.create_script(modify_info=modify_info,
                          record_path=record_path)

        # Run the shell script by oracle user.
        handle_path = '{head} @{path}'.\
            format(head=self.handle_head,
                   path=script_path)

        pip = subprocess.Popen(args=handle_path,
                               shell=True,
                               creationflags=subprocess.CREATE_NEW_CONSOLE)
        pip.wait()

        # Get the oracle information.
        while not os.path.exists(record_path):
            time.sleep(1)
        with open(record_path, 'r') as fip:
            instance_name = fip.readline().strip()

        # Delete the expire file.
        if instance_name:
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

        # Make the shell script path.
        script_name = 'show_trace_path.sql'
        record_name = 'show_trace_path.log'
        script_path = self.oracle_home + script_name
        record_path = self.oracle_home + record_name

        # Create and edit the shell script.
        shm.script_path = script_path

        modify_info = 'select value from v$dia' \
                      'g_info where name = \'Dia' \
                      'g Trace\';'
        log.debug(modify_info)
        shm.create_script(modify_info=modify_info,
                          record_path=record_path)

        # Run the shell script by oracle user.
        handle_path = '{head} @{path}'.\
            format(head=self.handle_head,
                   path=script_path)

        pip = subprocess.Popen(args=handle_path,
                               shell=True,
                               creationflags=subprocess.CREATE_NEW_CONSOLE)
        pip.wait()

        # Get the oracle information.
        while not os.path.exists(record_path):
            time.sleep(1)
        with open(record_path, 'r') as fip:
            trace_path = fip.readline().strip()

        # Delete the expire file.
        if trace_path:
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

        alert_path = trace_path + '\\'
        alert_path += 'alert_' + instance_name + '.log'
        if not os.path.exists(alert_path):
            return '0'

        # Get option values from configuration.
        config_path = 'C:\\dam' + 'g\\etc\\dam' + 'g.conf'
        cfg = configparser.ConfigParser()
        cfg.read(config_path)

        try:
            health_time = cfg.get("oracle", "health_time")
        except Exception as e:
            log.debug(e)
            health_time = '30'

        # Get time information 3 month ago.
        source_time = time.time()
        target_time = int(source_time) - 86400 * int(health_time)
        verify_time = time.strftime("%a %b %d", time.localtime(target_time))
        verify_hour = time.strftime("%Y", time.localtime(target_time))

        error_count = 0
        check_stat = 0

        with open(alert_path, 'r') as fip:
            alert_list = fip.readlines()

            for inf in alert_list:
                if check_stat == 0:
                    if verify_time in inf and verify_hour in inf:
                        check_stat = 1
                    else:
                        continue
                else:
                    if 'TNS-' in inf:
                        error_count += 1
                    elif 'ORA-' in inf:
                        error_count += 1
                    elif 'error' in inf:
                        error_count += 1

        if error_count == 0:
            return '0'
        else:
            return '1'


class SystemManage(object):
    """
    Class about system operations.
    :method obtain_date_time:
    :method obtain_cpu_usage:
    :method obtain_mem_usage:
    :method obtain_ios_total:
    """
    logger_inst = None

    def __init__(self):
        self.logger_inst = _LOGGER_INST

    def obtain_sys_size(self):
        """
        Method to get the system size information.
        :return:                    used size
        :return:                    total size
        """
        log = self.logger_inst
        device_size = 0
        device_used = 0

        global _COLLECT_MAX
        global _COLLECT_NUM
        _COLLECT_MAX += 1

        # Get disk object list.
        try:
            object_list = psutil.disk_partitions()
        except Exception as e:
            log.debug(e)
            return '0|0'

        # Add the disk size together.
        for dev in object_list:
            if 'rw' not in dev.opts:
                continue
            else:
                device_name = dev.device
                device_size += psutil.disk_usage(device_name).total
                device_used += psutil.disk_usage(device_name).used

        # Return GB size.
        used_size = str(round(device_used / 1073741824, 2))
        total_size = str(round(device_size / 1073741824, 2))
        return_info = used_size + "|" + total_size
        _COLLECT_NUM += 1

        return return_info

    def obtain_instance_num(self):
        """
        Method to get the oracle instance number.
        :return:                    instance num
        """
        log = self.logger_inst
        locale_code = _LOCALE_CODE

        global _COLLECT_MAX
        global _COLLECT_NUM
        _COLLECT_MAX += 1

        obtain_info = 'task' + 'list' \
                      ' |find /i \"oracle\" /c'
        log.debug(obtain_info)

        pip = subprocess.Popen(args=obtain_info,
                               stdout=subprocess.PIPE,
                               stderr=subprocess.STDOUT,
                               creationflags=subprocess.CREATE_NEW_CONSOLE,
                               shell=True)
        pip.wait()

        return_info = pip.stdout.read().decode(locale_code).strip()
        if return_info:
            _COLLECT_NUM += 1

        return return_info

    def obtain_network_max(self):
        """
        Method to get the max network rate number.
        :return:                    rate num
        """
        log = self.logger_inst
        speed_max = 0

        global _COLLECT_MAX
        global _COLLECT_NUM
        _COLLECT_MAX += 1

        # Get the max network rate number.
        try:
            network_list = psutil.net_if_stats()
        except Exception as e:
            log.debug(e)
        else:
            for key, val in network_list.items():
                if val.speed % 1000 == 0:
                    speed_info = val.speed

                    if speed_info > speed_max:
                        speed_max = speed_info

        if speed_max != 0:
            _COLLECT_NUM += 1

        return speed_max

    def obtain_session_num(self):
        """
        Method to get session number.
        :return:                    session number
        """
        log = self.logger_inst
        record_path = 'C:\\dam' + 'g\\data\\high_frequency.json'
        session_max = 0

        global _COLLECT_MAX
        global _COLLECT_NUM
        _COLLECT_MAX += 1

        # Read the json information.
        if os.path.exists(record_path):
            with open(record_path, 'r') as fp:
                origin_list = json.load(fp)
        else:
            origin_list = []

        # Get the max session number.
        for obj in origin_list:
            try:
                session_num = int(obj['session'])
            except Exception as e:
                log.debug(e)
            else:
                if session_num > session_max:
                    session_max = session_num

        if session_max != 0:
            _COLLECT_NUM += 1

        # Return information.
        return_info = str(session_max)
        return return_info

    def obtain_process_num(self):
        """
        Method to get process number.
        :return:                    process number
        """
        log = self.logger_inst
        record_path = 'C:\\dam' + 'g\\data\\high_frequency.json'
        process_max = 0

        global _COLLECT_MAX
        global _COLLECT_NUM
        _COLLECT_MAX += 1

        # Read the json information.
        if os.path.exists(record_path):
            with open(record_path, 'r') as fp:
                origin_list = json.load(fp)
        else:
            origin_list = []

        # Get the max process number.
        for obj in origin_list:
            try:
                process_num = int(obj['process'])
            except Exception as e:
                log.debug(e)
            else:
                if process_num > process_max:
                    process_max = process_num

        if process_max != 0:
            _COLLECT_NUM += 1

        # Return information.
        return_info = str(process_max)
        return return_info


class ModuleManage(object):
    """
    Class about module operations.
    :method obtain_object:
    """
    oracle_user = []
    oracle_home = ''
    record_path = 'low_frequency.json'

    def __init__(self, option_dict):
        self.oracle_user = option_dict['usr']
        self.oracle_home = 'C:\\dam'+'g\\tmp\\'
        record_home = 'C:\\dam'+'g\\data\\'
        self.record_path = record_home + '\\low_frequency.json'

        if not os.path.exists(self.oracle_home):
            os.makedirs(self.oracle_home)
        if not os.path.exists(record_home):
            os.makedirs(record_home)

        if option_dict['out'] == 'no':
            global _MANUAL_STAT
            _MANUAL_STAT = 'no'

    def obtain_object(self):
        """
        Method to record the object relation information.
        :return:
        """
        oracle_user = self.oracle_user
        oracle_home = self.oracle_home
        return_inst = {}
        oracle_inst = {}
        system_inst = {}

        # Make the module logger function.
        lgm = LoggerManage()
        lgm.create_logger()
        log = _LOGGER_INST

        # Get system size.
        if _MANUAL_STAT == 'yes':
            print('Collecting information about system total/used size ...')
        stm = SystemManage()
        system_size = stm.obtain_sys_size()
        log.debug(system_size)
        used_size = system_size.split('|')[0]
        total_size = system_size.split('|')[1]
        system_inst.update({"fs_size": total_size})
        system_inst.update({"fs_used": used_size})

        # Get oracle instance number.
        if _MANUAL_STAT == 'yes':
            print('Collecting information about instance number ...')
        instance_num = stm.obtain_instance_num()
        log.debug(instance_num)
        oracle_inst.update({"instance_num": instance_num})

        # Get oracle session number.
        if _MANUAL_STAT == 'yes':
            print('Collecting information about session number ...')
        session_num = stm.obtain_session_num()
        log.debug(session_num)
        oracle_inst.update({"session_num": session_num})

        # Get oracle process number.
        if _MANUAL_STAT == 'yes':
            print('Collecting information about process number ...')
        process_num = stm.obtain_process_num()
        log.debug(process_num)
        oracle_inst.update({"process_num": process_num})

        # Get system core number.
        if _MANUAL_STAT == 'yes':
            print('Collecting information about core number ...')
        core_num = psutil.cpu_count()
        log.debug(core_num)
        oracle_inst.update({"core_num": str(core_num)})

        # Get max network rate number.
        if _MANUAL_STAT == 'yes':
            print('Collecting information about max network rate ...')
        network_max = 0
        for key, val in psutil.net_if_stats().items():
            if val.speed > network_max:
                network_max = val.speed
        log.debug(network_max)
        system_inst.update({"max_net_rate": network_max})

        # Get oracle size.
        if _MANUAL_STAT == 'yes':
            print('Collecting information about db size ...')
        ocm = OracleManage(oracle_home=oracle_home,
                           oracle_user=oracle_user[0])
        oracle_size = ocm.obtain_oracle_size()
        log.debug(oracle_size)
        system_inst.update({"db_size": oracle_size})

        # Get oracle data size.
        if _MANUAL_STAT == 'yes':
            print('Collecting information about data size ...')
        oracle_used = ocm.obtain_data_size()
        log.debug(oracle_used)
        system_inst.update({"data_size": oracle_used})

        # Get oracle version.
        if _MANUAL_STAT == 'yes':
            print('Collecting information about db version ...')
        oracle_ver = ocm.obtain_version()
        log.debug(oracle_ver)
        oracle_inst.update({"db_version": oracle_ver})

        # Get database information.
        if _MANUAL_STAT == 'yes':
            print('Collecting information about db name & id & log mode ...')
        database_info = ocm.obtain_database()
        log.debug(database_info)
        db_code = database_info.split('|')[0]
        db_name = database_info.split('|')[1]
        log_mode = database_info.split('|')[2]
        oracle_inst.update({"db_id": db_code})
        oracle_inst.update({"db_name": db_name})
        oracle_inst.update({"log_mode": log_mode})

        # Get oracle health status.
        if _MANUAL_STAT == 'yes':
            print('Collecting information about db health ...')
        oracle_health = ocm.obtain_health()
        log.debug(oracle_health)
        oracle_inst.update({"db_health": oracle_health})

        # Get sga size.
        if _MANUAL_STAT == 'yes':
            print('Collecting information about sga/pga size ...')
        sga_size = ocm.obtain_sga_size()
        log.debug(sga_size)
        oracle_inst.update({"sga_size": sga_size})

        # Get pga size.
        pga_size = ocm.obtain_pga_size()
        log.debug(pga_size)
        oracle_inst.update({"pga_size": pga_size})

        # Get number of transaction object.
        if _MANUAL_STAT == 'yes':
            print('Collecting information about transaction number ...')
        object_num = ocm.obtain_tran_num()
        log.debug(object_num)
        oracle_inst.update({"transaction_num": object_num})

        # Get oracle db files number.
        if _MANUAL_STAT == 'yes':
            print('Collecting information about db files ...')
        db_file_num = ocm.obtain_db_files()
        log.debug(db_file_num)
        oracle_inst.update({"db_files": db_file_num})

        # Get object information.
        schema_inst_list = []
        for usr in oracle_user:
            schema_inst = {}
            ocm.oracle_user = usr

            if _MANUAL_STAT == 'yes':
                print('Collecting information about object relation ...')
            object_type_list = []
            object_type = ocm.obtain_object_type()
            if object_type:
                for typ in object_type:
                    single_type = typ.rstrip()

                    object_name_list = []
                    ret = ocm.obtain_object_name(single_type)
                    if ret:
                        for obj in ret:
                            single_info = obj.rstrip()
                            object_name_list.append(single_info)

                    object_info = {}
                    object_info.update({"object_type": single_type})
                    object_info.update({"object_name": object_name_list})
                    object_type_list.append(object_info)

            if _MANUAL_STAT == 'yes':
                print('Collecting information about object size ...')
            object_size_list = []
            object_size = ocm.obtain_object_size()
            if object_size:
                for obj in object_size:
                    single_info = obj.strip()
                    if single_info:
                        opt = single_info.split('|')[0]
                        try:
                            val = single_info.split('|')[1]
                        except IndexError:
                            continue

                        try:
                            val = str(round(int(val) / 1073741824, 2))
                        except ValueError:
                            continue

                        object_info = {}
                        object_info.update({"option": opt})
                        object_info.update({"value": val})
                        object_size_list.append(object_info)

            if _MANUAL_STAT == 'yes':
                print('Collecting information about materialized view ...')
            object_num = ocm.obtain_view_num()

            # Get oracle segment number.
            if _MANUAL_STAT == 'yes':
                print('Collecting information about segment number ...')
            segment_num = ocm.obtain_segment_num()

            # Get oracle object type number.
            if _MANUAL_STAT == 'yes':
                print('Collecting information about object type number ...')
            obj_type_num = ocm.obtain_obj_type_num()

            schema_inst.update({'schema_name': usr})
            schema_inst.update({"segment_num": segment_num})
            schema_inst.update({"object_type_num": obj_type_num})
            schema_inst.update({'object_list': object_type_list})
            schema_inst.update({'object_size': object_size_list})
            schema_inst.update({'materialized_view_num': object_num})
            schema_inst_list.append(schema_inst)
        oracle_inst.update({"schema_list": schema_inst_list})

        # Get object link information.
        if _MANUAL_STAT == 'yes':
            print('Collecting information about db links ...')
        schema_link_list = []
        for usr in oracle_user:
            ocm.oracle_user = usr

            object_link_list = ocm.obtain_object_link()
            if object_link_list:
                for ext in object_link_list:
                    object_info = ext.rstrip()
                    object_user = object_info.split('|')[0]
                    object_link = object_info.split('|')[1]
                    object_host = object_info.split('|')[2]

                    object_inst = {}
                    object_inst.update({"schema_name": usr})
                    object_inst.update({"user_name": object_user})
                    object_inst.update({"db_link": object_link})
                    object_inst.update({"description": object_host})
                    schema_link_list.append(object_inst)
        oracle_inst.update({"schema_link": schema_link_list})

        # Get wait event information.
        if _MANUAL_STAT == 'yes':
            print('Collecting information about wait events ...')
        wait_event_list = []
        wait_event = ocm.obtain_wait_event()
        for eve in wait_event:
            single_info = eve.rstrip()
            event_info = single_info.split('|')[0]
            total_wait = single_info.split('|')[1]
            avg_wait = single_info.split('|')[2]
            wait_type = single_info.split('|')[3]

            object_inst = {}
            object_inst.update({"event_info": event_info})
            object_inst.update({"total_wait": total_wait})
            object_inst.update({"avg_wait": avg_wait})
            object_inst.update({"wait_type": wait_type})
            wait_event_list.append(object_inst)
        oracle_inst.update({"wait_event": wait_event_list})

        # Collect the low frequency information.
        return_inst.update({"system": system_inst})
        return_inst.update({"oracle": oracle_inst})

        # Write down the json information.
        return_json = json.dumps(return_inst)
        with open(self.record_path, 'w') as fip:
            fip.writelines(str(return_json))

        # Record degree information.
        record_degree()

        return None


if __name__ == '__main__':
    mmm = ModuleManage({'usr': ['SYSTEM'], 'out': 'yes'})
    mmm.obtain_object()
