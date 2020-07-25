import logging
import os
import subprocess

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


class SystemManage(object):
    """
    Class about system operations.
    :method obtain_object:
    """
    oracle_user = ''
    record_path = ''
    logger_inst = None

    def __init__(self, oracle_user, record_path):
        """
        Method to build a system object.
        :param record_path:         record path
        """
        self.oracle_user = oracle_user
        self.record_path = record_path
        self.logger_inst = _LOGGER_INST

    def obtain_object(self):
        """
        Method to get readable information.
        :return:                    none
        """
        log = self.logger_inst
        origin_path = self.record_path + self.oracle_user + '.ddl1'
        target_path = self.record_path + self.oracle_user + '.ddl'

        # Delete the origin dmp file.
        if os.path.exists(origin_path):
            os.remove(origin_path)

        # Run the information to get bin file.
        obtain_file = 'exp \"\'/ as sys' \
                      'dba\'\" file={path} buffer=5120000' \
                      ' rows=n statistics=none owner={user}\n'\
            .format(path=origin_path,
                    user=self.oracle_user)
        log.debug(obtain_file)

        pip = subprocess.Popen(args=obtain_file,
                               shell=True,
                               creationflags=subprocess.CREATE_NEW_CONSOLE)
        pip.wait()

        # Get the readable record file.
        change_file = 'C:\\dam' + 'g\\tools\\strings64.exe {src} >{tgt}'\
            .format(src=origin_path,
                    tgt=target_path)
        log.debug(change_file)

        pip = subprocess.Popen(args=change_file,
                               shell=True,
                               creationflags=subprocess.CREATE_NEW_CONSOLE)
        pip.wait()

        # Remove the tmp bin file.
        if os.path.exists(origin_path):
            os.remove(origin_path)

        return None


class ModuleManage(object):
    """
    Class about module operations.
    :method obtain_object:
    """
    oracle_user = []
    record_home = ''

    def __init__(self, option_dict):
        """
        Method to build a module object.
        :param option_dict:         option dictionary
        """
        self.oracle_user = option_dict['usr']
        self.record_home = 'C:\\dam'+'g\\data\\'

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
            print('Collecting information about ddl ...')

        # Get the ddl information.
        for usr in self.oracle_user:
            oracle_user = usr

            # Get oracle object information.
            smm = SystemManage(oracle_user=oracle_user,
                               record_path=self.record_home)
            smm.obtain_object()

        return None


if __name__ == '__main__':
    mmm = ModuleManage({'usr': ['SYSTEM'], 'out': 'yes'})
    mmm.obtain_object()
