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
        :return:                    none
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

    def modify_script(self, oracle_user):
        """
        Method to modify the specified shell script.
        :param oracle_user:         oracle user
        :return:                    none
        """
        script_info = 'exp \"\'/ as sys' \
                      'dba\'\" file={user}.ddl buffer=5120000' \
                      ' rows=n statistics=none owner={user}\n'\
            .format(user=oracle_user)

        with open(file=self.script_path,
                  mode='w+') as fip:
            fip.writelines('#!/bin/sh\n')
            fip.writelines(script_info)
            fip.writelines('exit 0\n')

        return None

    def delete_script(self):
        """
        Method to delete the specified shell script.
        :return:                    none
        """
        if os.path.exists(self.script_path):
            os.remove(self.script_path)

        return None


class SystemManage(object):
    """
    Class about system operations.
    :method obtain_date_time:
    """
    object_path = ''
    logger_inst = None

    def __init__(self, object_path):
        """
        Method to build a system object.
        :param object_path:         object path
        """
        self.object_path = object_path
        self.logger_inst = _LOGGER_INST

    def create_record(self, origin_path):
        """
        Method to get readable information.
        :return:                    none
        """
        log = self.logger_inst

        # Get the readable record file.
        change_info = 'strings {src} >{tgt} 2>/dev/null'\
            .format(src=origin_path,
                    tgt=self.object_path)
        log.debug(change_info)
        os.system(change_info)

        # Delete the origin dmp file.
        delete_orig = 'rm -f {src} >/dev/null 2>&1'\
            .format(src=origin_path)
        os.system(delete_orig)

        return None


class OracleManage(object):
    """
    Class about oracle operations.
    :method obtain_object:
    """
    oracle_home = ''
    oracle_user = ''
    logger_inst = None

    def __init__(self, oracle_home, oracle_user):
        """
        Method to build an oracle object.
        :param oracle_home:         oracle home path
        :param oracle_user:         oracle user
        """
        self.oracle_home = oracle_home
        self.oracle_user = oracle_user
        self.logger_inst = _LOGGER_INST

    def obtain_object(self):
        """
        Method to get object ddl list.
        :return:                    none
        """
        log = self.logger_inst

        # Make the shell script path.
        script_name = '.list_ddl.sh'
        script_path = self.oracle_home + script_name
        log.debug(script_path)

        # Create and edit the shell script.
        shm = ScriptManage(script_path)
        shm.create_script()
        shm.modify_script(self.oracle_user)

        # Run the shell script by oracle user.
        handle_path = 'su - oracle -c \'{path}\' >/dev/null 2>&1'\
            .format(path=script_path)
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
    record_home = ''

    def __init__(self, option_dict):
        """
        Method to build a module object.
        :param option_dict:         option dictionary
        """
        self.oracle_user = option_dict['usr']

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
            print('Collecting information about ddl ...')

        # Get the ddl information.
        for usr in self.oracle_user:
            oracle_user = usr.upper()

            # Get oracle object information.
            ocm = OracleManage(oracle_home=self.oracle_home,
                               oracle_user=oracle_user)
            ocm.obtain_object()

            # Record the ddl information.
            target_path = self.record_home + oracle_user + '.ddl'
            stm = SystemManage(target_path)

            source_path = self.oracle_home + oracle_user + '.ddl'
            stm.create_record(source_path)

        return None


if __name__ == '__main__':
    mmm = ModuleManage({'usr': ['SYS'],
                        'pwd': '/home/oracle',
                        'out': 'yes'})
    mmm.obtain_object()
