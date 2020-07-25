import logging
import os
import subprocess
import time

_LOGGER_INST = None
_MANUAL_STAT = 'yes'


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
            fip.writelines('set lines 20480;\n')
            fip.writelines('spool ' + record_path + ';\n')
            fip.writelines(modify_info + '\n')
            fip.writelines('spool off;\n')
            fip.writelines('exit;\n')

        return None


class OracleManage(object):
    """
    Class about oracle operations.
    :method obtain_object:
    """
    source_time = ''
    oracle_user = ''
    oracle_home = ''
    handle_head = 'start /b sql' + 'plus / as sys' + 'dba'
    logger_inst = None

    def __init__(self, source_time,
                 oracle_user, oracle_home):
        """
        Method to build an oracle object.
        :param source_time:         time when the environment built
        :param oracle_user:         oracle user
        :param oracle_home:         oracle home path
        """
        self.source_time = source_time
        self.oracle_user = oracle_user
        self.oracle_home = oracle_home
        self.logger_inst = _LOGGER_INST

    def obtain_object(self, record_path):
        """
        Method to get object type.
        :param record_path:         record path
        :return:                    none
        """
        log = self.logger_inst

        # Make the shell script path.
        script_name = 'show_dml.sql'
        script_path = self.oracle_home + script_name

        # Get the target time string information.
        string_list = self.source_time.split('-')
        target_year = str(int(string_list[0])+1)
        target_time = target_year + '-' + string_list[1] + '-'
        target_time += string_list[2]

        # Create and edit the shell script.
        shm = ScriptManage(script_path)

        modify_info = 'select sql_id|| \'|\' ||first_load_time|| \'|\'' \
                      ' ||executions|| \'|\' ||module|| \'|\'' \
                      ' ||to_char(sql_text) from v$sql' \
                      'area where command_type not in (3,47)' \
                      ' and parsing_schema_name=\'{usr}\'' \
                      ' and module is not null' \
                      ' and first_load_time between' \
                      ' \'{beg}\' and \'{end}\'' \
                      ' order by first_load_time;' \
            .format(usr=self.oracle_user,
                    beg=self.source_time,
                    end=target_time)
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

        # Delete the expire file.
        while True:
            if os.path.exists(record_path):
                if os.path.exists(script_path):
                    try:
                        os.remove(script_path)
                    except PermissionError:
                        pass
                    else:
                        break
            time.sleep(1)

        return None


class ModuleManage(object):
    """
    Class about module operations.
    :method obtain_object:
    """
    oracle_user = []
    source_time = ''
    oracle_home = ''
    record_home = ''

    def __init__(self, option_dict):
        """
        Method to build a module object.
        :return:
        """
        self.oracle_user = option_dict['usr']
        self.source_time = option_dict['day']
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
        # Make the module logger function.
        lgm = LoggerManage()
        lgm.create_logger()

        if _MANUAL_STAT == 'yes':
            print('Collecting information about dml ...')

        # Get the dml information.
        for usr in self.oracle_user:
            oracle_user = usr
            record_path = self.record_home + oracle_user + '.dml'

            # Get oracle object information.
            ocm = OracleManage(oracle_home=self.oracle_home,
                               oracle_user=oracle_user,
                               source_time=self.source_time)
            ocm.obtain_object(record_path)

        return None


if __name__ == '__main__':
    test_dict = {'usr': ['SYSTEM'],
                 'day': '2020-01-01/01:00:00',
                 'out': 'yes'}
    mmm = ModuleManage(test_dict)
    mmm.obtain_object()
