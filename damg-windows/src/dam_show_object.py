import configparser
import json
import logging
import os
import subprocess
import time

_LOGGER_INST = None
_MANUAL_STAT = 'yes'
_COLLECT_MAX = 0
_COLLECT_NUM = 0


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

        return None


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
    :method obtain_object:
    """
    oracle_user = ''
    oracle_home = ''
    handle_head = 'start /B sql' + 'plus / as sys' + 'dba'
    logger_inst = None

    def __init__(self, oracle_user, oracle_home):
        self.oracle_user = oracle_user
        self.oracle_home = oracle_home
        self.logger_inst = _LOGGER_INST

    def obtain_index(self):
        """
        Method to get object relationship.
        :return:                    object relationship list
        """
        log = self.logger_inst

        global _COLLECT_MAX
        global _COLLECT_NUM
        _COLLECT_MAX += 1

        # Make the shell script path.
        script_name = 'list_obj_index.sql'
        record_name = 'list_obj_index.log'
        script_path = self.oracle_home + script_name
        record_path = self.oracle_home + record_name

        # Create and edit the shell script.
        shm = ScriptManage(script_path)

        manage_info = 'select table_name||\'|\'||index_name||\'|\'' \
                      '||to_char(wm_concat(column_name)) as column_list' \
                      ' from dba_ind_columns where index_owner=\'{user}\'' \
                      ' group by table_name, index_name;' \
            .format(user=self.oracle_user)
        log.debug(manage_info)

        shm.create_script(modify_info=manage_info,
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

    def obtain_lob(self):
        """
        Method to get object relationship.
        :return:                    object relationship list
        """
        log = self.logger_inst

        global _COLLECT_MAX
        global _COLLECT_NUM
        _COLLECT_MAX += 1

        # Make the shell script path.
        script_name = 'list_obj_lob.sql'
        record_name = 'list_obj_lob.log'
        script_path = self.oracle_home + script_name
        record_path = self.oracle_home + record_name

        # Create and edit the shell script.
        shm = ScriptManage(script_path)

        manage_info = 'select table_name||\'|\'||column_name||\'|\'||' \
                      'segment_name||\'|\'||tablespace_name from' \
                      ' dba_lobs where owner=\'{user}\';'\
            .format(user=self.oracle_user)
        log.debug(manage_info)

        shm.create_script(modify_info=manage_info,
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

    def obtain_trigger(self):
        """
        Method to get object relationship.
        :return:                    object relationship list
        """
        log = self.logger_inst

        global _COLLECT_MAX
        global _COLLECT_NUM
        _COLLECT_MAX += 1

        # Make the shell script path.
        script_name = 'list_obj_trigger.sql'
        record_name = 'list_obj_trigger.log'
        script_path = self.oracle_home + script_name
        record_path = self.oracle_home + record_name

        # Create and edit the shell script.
        shm = ScriptManage(script_path)

        manage_info = 'select table_name||\'|\'||trigger_name||\'|\'||' \
                      'to_char(wm_concat(column_name)) as column_list' \
                      ' from dba_trigger_cols where trigger_owner=\'{user}\'' \
                      ' group by table_name, trigger_name;'\
            .format(user=self.oracle_user)
        log.debug(manage_info)

        shm.create_script(modify_info=manage_info,
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

    def obtain_view(self):
        """
        Method to get object relationship.
        :return:                    object relationship list
        """
        log = self.logger_inst

        global _COLLECT_MAX
        global _COLLECT_NUM
        _COLLECT_MAX += 1

        # Make the shell script path.
        script_name = 'list_obj_view.sql'
        record_name = 'list_obj_view.log'
        script_path = self.oracle_home + script_name
        record_path = self.oracle_home + record_name

        # Create and edit the shell script.
        shm = ScriptManage(script_path)

        manage_info = 'select name||\'|\'||referenced_name' \
                      '||\'|\'||referenced_type from dba_dependencies' \
                      ' where owner=\'{user}\' and TYPE=\'VIEW\';'\
            .format(user=self.oracle_user)
        log.debug(manage_info)

        shm.create_script(modify_info=manage_info,
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


class ModuleManage(object):
    """
    Class about module operations.
    :method obtain_object:
    """
    oracle_user = []
    oracle_home = ''
    record_home = ''

    def __init__(self, option_dict):
        """
        Method to build a module object.
        :return:
        """
        self.oracle_user = option_dict['usr']
        self.oracle_home = 'C:\\dam'+'g\\tmp\\'
        self.record_home = 'C:\\dam'+'g\\data\\'

        if not os.path.exists(self.oracle_home):
            os.makedirs(self.oracle_home)
        if not os.path.exists(self.record_home):
            os.makedirs(self.record_home)

        if option_dict['out'] == 'no':
            global _MANUAL_STAT
            _MANUAL_STAT = 'no'

    def obtain_object(self):
        """
        Method to record the object relation information.
        :return:
        """
        schema_list = []
        record_path = self.record_home + 'object_relation.json'

        # Make the module logger function.
        lgm = LoggerManage()
        lgm.create_logger()
        log = _LOGGER_INST

        for usr in self.oracle_user:
            # Get oracle object information.
            ocm = OracleManage(oracle_home=self.oracle_home,
                               oracle_user=usr)

            # Get index information.
            if _MANUAL_STAT == 'yes':
                print('Collecting information about index object ...')

            return_list = ocm.obtain_index()
            if return_list:
                log.debug(return_list[0])

            object_inst = {}
            object_list = []
            for obj in return_list:
                single_info = obj.rstrip()

                table_name = single_info.split('|')[0]
                index_name = single_info.split('|')[1]
                column_list = single_info.split('|')[2]
                single_inst = {"table": table_name,
                               "index": index_name,
                               "column": column_list}
                object_list.append(single_inst)

            object_inst.update({'schema_name': usr})
            object_inst.update({'object_type': 'index'})
            object_inst.update({'object_info': object_list})
            schema_list.append(object_inst)

            # Get lob information.
            if _MANUAL_STAT == 'yes':
                print('Collecting information about lob object ...')

            return_list = ocm.obtain_lob()
            if return_list:
                log.debug(return_list[0])

            object_inst = {}
            object_list = []
            for obj in return_list:
                single_info = obj.rstrip()

                table_name = single_info.split('|')[0]
                column_name = single_info.split('|')[1]
                segment_name = single_info.split('|')[2]
                tablespace_name = single_info.split('|')[3]
                single_inst = {"table": table_name,
                               "column": column_name,
                               "segment": segment_name,
                               "tablespace": tablespace_name}
                object_list.append(single_inst)

            object_inst.update({'schema_name': usr})
            object_inst.update({'object_type': 'lob'})
            object_inst.update({'object_info': object_list})
            schema_list.append(object_inst)

            # Get trigger information.
            if _MANUAL_STAT == 'yes':
                print('Collecting information about trigger object ...')

            return_list = ocm.obtain_trigger()
            if return_list:
                log.debug(return_list[0])

            object_inst = {}
            object_list = []
            for obj in return_list:
                single_info = obj.rstrip()

                table_name = single_info.split('|')[0]
                trigger_name = single_info.split('|')[1]
                column_list = single_info.split('|')[2]
                single_inst = {"table": table_name,
                               "trigger": trigger_name,
                               "column": column_list}
                object_list.append(single_inst)

            object_inst.update({'schema_name': usr})
            object_inst.update({'object_type': 'trigger'})
            object_inst.update({'object_info': object_list})
            schema_list.append(object_inst)

            # Get view information.
            if _MANUAL_STAT == 'yes':
                print('Collecting information about view object ...')

            return_list = ocm.obtain_view()
            if return_list:
                log.debug(return_list[0])

            object_inst = {}
            object_list = []
            for obj in return_list:
                single_info = obj.rstrip()

                view_name = single_info.split('|')[0]
                referenced_name = single_info.split('|')[1]
                referenced_type = single_info.split('|')[2]
                single_inst = {"view": view_name,
                               "rel_name": referenced_name,
                               "rel_type": referenced_type}
                object_list.append(single_inst)

            object_inst.update({'schema_name': usr})
            object_inst.update({'object_type': 'view'})
            object_inst.update({'object_info': object_list})
            schema_list.append(object_inst)

        # Write down the json information.
        object_json = json.dumps(schema_list)
        with open(record_path, 'w') as fip:
            fip.writelines(str(object_json))

        # Record degree information.
        record_degree()

        return None


if __name__ == '__main__':
    mmm = ModuleManage({'usr': ['SYSTEM'], 'out': 'yes'})
    mmm.obtain_object()
