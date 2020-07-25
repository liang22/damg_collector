import logging
import os
import stat

_LOGGER_INST = None
_MANUAL_STAT = 'yes'


class LoggerManage(object):
    """
    Class about functions to operate the log information.
    :method create_logger:
    """
    logger_home = '/var/log/DAM' + 'G/'
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
    :method modify_script(modify_info):
    :method delete_script:
    """
    script_path = ''

    def __init__(self, script_path):
        """
        Method to build a script object.
        :param script_path:         script path
        """
        self.script_path = script_path

    def create_script(self):
        """
        Method to create a shell script(777).
        :return:                    none
        """
        permit_code = stat.S_IRWXU + stat.S_IRWXG + stat.S_IRWXO

        # Create and chmod the shell script path.
        if not os.path.exists(self.script_path):
            os.mknod(self.script_path)
        os.chmod(path=self.script_path,
                 mode=permit_code)

        return None

    def modify_script(self, modify_info):
        """
        Method to modify the specified shell script.
        :param modify_info:         modify information
        :return:                    none
        """
        with open(file=self.script_path,
                  mode='w+') as fip:
            fip.writelines('sql' + 'plus -S -L /nolog<<EOF\n')
            fip.writelines('connect / as sys' + 'dba\n')
            fip.writelines('set term' + 'out off;\n')
            fip.writelines('set echo off;\n')
            fip.writelines('set feedback off;\n')
            fip.writelines('set heading off;\n')
            fip.writelines('set pagesize 0;\n')
            fip.writelines('set lines 20480;\n')
            fip.writelines(modify_info+'\n')
            fip.writelines('quit\n')
            fip.writelines('EOF\n')

        return None

    def delete_script(self):
        """
        Method to delete the specified shell script.
        :return:                    none
        """
        if os.path.exists(self.script_path):
            os.remove(self.script_path)

        return None


class OracleManage(object):
    """
    Class about oracle operations.
    :method obtain_object:
    """
    source_time = ''
    oracle_user = ''
    oracle_home = ''
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
        script_name = '.show_dml.sh'
        script_path = self.oracle_home + script_name
        log.debug(script_path)

        # Get the target time string information.
        string_list = self.source_time.split('-')
        target_year = str(int(string_list[0])+1)
        target_time = target_year + '-' + string_list[1] + '-' + string_list[2]

        # Create and edit the shell script.
        shm = ScriptManage(script_path)
        shm.create_script()

        modify_info = 'select sql_id|| \'|\' ||first_load_time|| \'|\'' \
                      ' ||executions|| \'|\' ||module|| \'|\'' \
                      ' ||to_char(sql_text) from v\\$sql' \
                      'area where command_type not in (3,47)' \
                      ' and parsing_schema_name=\'{usr}\'' \
                      ' and module is not null' \
                      ' and first_load_time between' \
                      ' \'{beg}\' and \'{end}\'' \
                      ' order by first_load_time;'\
            .format(usr=self.oracle_user,
                    beg=self.source_time,
                    end=target_time)
        shm.modify_script(modify_info)

        # Run the shell script by oracle user.
        handle_path = 'su - oracle -c \'{exe}\' >{log}'.\
            format(exe=script_path,
                   log=record_path)
        os.system(handle_path)

        # Delete the tmp script.
        shm.delete_script()

        return None


class ModuleManage(object):
    """
    Class about module operations.
    :method obtain_object:
    """
    oracle_user = []
    oracle_home = ''
    source_time = ''
    record_home = ''

    def __init__(self, option_dict):
        """
        Method to build a module object.
        :return:
        """
        self.oracle_user = option_dict['usr']
        self.source_time = option_dict['day']

        if option_dict['pwd'][-1] != '/':
            self.oracle_home = option_dict['pwd'] + '/'
        else:
            self.oracle_home = option_dict['pwd']

        record_home = '/root/DAM' + 'G/'
        self.record_home = record_home
        if not os.path.exists(record_home):
            os.makedirs(record_home)

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
            oracle_user = usr.upper()
            record_path = self.record_home + oracle_user + '.dml'

            # Get oracle object information.
            ocm = OracleManage(oracle_home=self.oracle_home,
                               oracle_user=oracle_user,
                               source_time=self.source_time)
            ocm.obtain_object(record_path)

        return None


if __name__ == '__main__':
    test_dict = {'usr': ['SYS'],
                 'day': '2020-06-08/13:52:54',
                 'pwd': '/home/oracle',
                 'out': 'yes'}
    mmm = ModuleManage(test_dict)
    mmm.obtain_object()
