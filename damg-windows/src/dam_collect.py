import argparse
import configparser
import logging
import os
import shutil
import sys
import time

import dam_low_frequency
import dam_show_object
import dam_show_ddl
import dam_show_dml
import dam_show_dql

_LOGGER_INST = None
_HANDLE_DICT = {'packed_stat': 'yes',
                'manual_stat': 'yes'}

_INFO_ENABLE_LAYOUT = 'Start to collect information.'
_ERROR_SERVER_EXCESS = 'ERROR: Server is busy, ' \
                       'please check the cpu & io status.'
_ERROR_ORACLE_EXCEPT = 'ERROR: Oracle or system environment exception.'
_ERROR_CONFIG_EXCEPT = 'ERROR: Configuration environment exception.'
_ERROR_ACTION_HANDLE = 'ERROR: Information is still collecting, ' \
                       'please wait later ...'


class LoggerManage(object):
    """
    Class about methods to operate the log information.
    :method create_logger:
    """
    logger_home = 'C:\\dam'+'g\\log\\'
    logger_name = 'collector.log'

    def create_logger(self):
        """
        Method to create a logger object.
        :return:
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


class ConfigManage(object):
    """
    Class about methods to read & write the configuration.
    :method create_logger:
    """
    sector_name = ''
    option_name = ''
    config_path = 'C:\\dam' + 'g\\etc\\dam' + 'g.conf'
    config_inst = None

    def __init__(self):
        """
        Method to build a config object.
        """
        cfg = configparser.ConfigParser()
        cfg.read(self.config_path)
        self.config_inst = cfg

    def effect_config(self):
        """
        Method to rewrite the configuration.
        :return:
        """
        cfg = self.config_inst
        cfg.write(open(self.config_path, "w+"))

        return None

    def reveal_normal(self, option_stat):
        """
        Method to get option value.
        :param option_stat:
        :return:
        """
        cfg = self.config_inst

        # Get the specified option value.
        try:
            val = cfg.get(self.sector_name, self.option_name)
        except configparser.NoSectionError:
            print(_ERROR_CONFIG_EXCEPT)
            print('Missing section \'' + self.sector_name + '\'.')
            sys.exit(0)
        except configparser.NoOptionError:
            print(_ERROR_CONFIG_EXCEPT)
            print('Missing option \'' + self.option_name + '\'.')
            sys.exit(0)

        # If option stat equals 1, the option value can't be empty.
        # If option stat equals 0, return the option value.
        if option_stat == 1:
            if val.strip() == '':
                print(_ERROR_CONFIG_EXCEPT)
                print('Empty option \'' + self.option_name + '\'.')
                sys.exit(0)

        return val

    def reveal_senior(self):
        """
        Method to get senior option value.
        :return:
        """
        cfg = self.config_inst

        try:
            val = cfg.get('process', self.option_name)
        except configparser.NoSectionError:
            val = 0
        except configparser.NoOptionError:
            val = 0

        return val

    def record_senior(self, option_info):
        """
        Method to set senior option value.
        :param option_info:
        :return:
        """
        cfg = self.config_inst

        # Setup the process option.
        try:
            cfg.set('process', self.option_name, option_info)
        except configparser.NoSectionError:
            cfg.add_section('process')
            cfg.set('process', self.option_name, option_info)

        # Rewrite the configuration.
        self.config_inst = cfg
        self.effect_config()

        return None


class SystemManage(object):
    """
    Class about methods to operate the system tools.
    """
    logger_inst = None

    def __init__(self):
        """
        Method to build a system object.
        """
        self.logger_inst = _LOGGER_INST

    def encode_object(self):
        """
        Method to encrypt the specified file.
        :return:
        """
        log = self.logger_inst
        vector_code = '688D01DC3C571B76BD91BED3D069336E'
        encode_code = '2E13C289C3C0C47A2267A7EB' + 'DE11D00D'
        encode_salt = 'qC1FDG0gtbT8CdqKTmHjGg'

        # Get desktop path.
        # Origin data file and encrypt data file.
        target_home = os.path.join(os.path.expanduser("~"), 'Desktop')
        source_path = target_home + '\\DAM' + 'G_INFO.zip'
        target_path = target_home + '\\DAM' + 'G_INFO.enc'

        # Wait until the zip file be created.
        while not os.path.exists(source_path):
            time.sleep(1)

        # Create the new encrypt package.
        encrypt_file = 'C:\\damg\\tools\\openssl.exe enc -aes-128-cbc' \
                       ' -in {src} -out {tgt}' \
                       ' -iv {vec} -K {key} -S {sal}'\
            .format(src=source_path,
                    tgt=target_path,
                    vec=vector_code,
                    key=encode_code,
                    sal=encode_salt)
        log.debug(encrypt_file)
        os.system(encrypt_file)

        return None

    def create_packet(self, schema_list):
        """
        Method to create the compress packet.
        :params schema_list:            schema user list
        :return:                        none
        """
        log = self.logger_inst

        # Get desktop path.
        # Origin data file and encrypt data file.
        target_home = os.path.join(os.path.expanduser("~"), 'Desktop')
        target_path = target_home + '\\DAM' + 'G_INFO.zip'
        source_home = 'C:\\dam' + 'g\\data\\'

        # Delete the expire zip file.
        if os.path.exists(target_path):
            os.remove(target_path)

        # Get user dxl path information.
        scheme_info = ''
        for usr in schema_list:
            scheme_info += source_home
            scheme_info += usr
            scheme_info += '.d* '

        # Create the new compress package.
        create_pack = 'C:\\damg\\tools\\zip.exe -r {tgt} {src}*.json {dxl}'\
            .format(tgt=target_path,
                    src=source_home,
                    dxl=scheme_info)
        log.debug(create_pack)
        os.system(create_pack)

        return None


def enable_module():
    """
    Function to start the collect module.
    :return:
    """
    listen_info = ''

    # Get option values from configuration.
    cfm = ConfigManage()
    cfm.sector_name = 'public'
    cfm.option_name = 'cycle_time'
    cycle_time = cfm.reveal_normal(1)

    cfm.option_name = 'listen_host'
    listen_host = cfm.reveal_normal(0)

    cfm.option_name = 'listen_pwd'
    listen_code = cfm.reveal_normal(0)

    # Get listen string information.
    if listen_host and listen_code:
        listen_info = ' /S {host} /U administrator /P {code}'\
            .format(host=listen_host,
                    code=listen_code)

    # Add schedule plan.
    stable_path = 'C:\\dam' + 'g\\bin\\run_stable.exe'
    single_path = 'C:\\dam' + 'g\\bin\\run_single.exe'
    series_path = 'C:\\dam' + 'g\\bin\\run_series.exe'

    extend_plan = 'sch' + 'tasks /create {info} /tn dam_high_single ' \
                  '/tr \"{path}\" /sc minute /mo 1'\
        .format(info=listen_info,
                path=single_path)
    os.system(extend_plan)

    extend_plan = 'sch' + 'tasks /create {info} /tn dam_high_series ' \
                  '/tr \"{path}\" /sc minute /mo 3'\
        .format(info=listen_info,
                path=series_path)
    os.system(extend_plan)

    extend_plan = 'sch' + 'tasks /create {info} /tn dam_collect ' \
                  '/tr \"{path}\" /sc DAILY /mo {time}'\
        .format(info=listen_info,
                path=stable_path,
                time=cycle_time)
    os.system(extend_plan)

    # Run the collect instruction without package built.
    global _HANDLE_DICT
    _HANDLE_DICT['packed_stat'] = 'no'

    # Run the exec function without print process information.
    layout_module()

    return None


def timing_module():
    """
    Function to run the collect module at once.
    :return:
    """
    global _HANDLE_DICT
    _HANDLE_DICT['manual_stat'] = 'no'

    # Get option values from configuration.
    cfm = ConfigManage()
    cfm.sector_name = 'public'
    cfm.option_name = 'cycle_time'
    circle_time = cfm.reveal_normal(1)

    # Set option value to configuration.
    cfm.option_name = 'cycle_count'
    circle_this = cfm.reveal_senior()

    if circle_this == circle_time:
        circle_this = '0'
    else:
        circle_this = str(int(circle_this)+1)
    cfm.record_senior(circle_this)

    # Run the exec function without print process information.
    layout_module()

    return None


def layout_module():
    """
    Function to run the collect module at once.
    :return:
    """
    log = _LOGGER_INST
    log.info(_INFO_ENABLE_LAYOUT)

    # Check if the server be busy.
    status_path = 'C:\\dam' + 'g\\log\\collect_stop'
    if os.path.exists(status_path):
        log.info(_ERROR_SERVER_EXCESS)
        print(_ERROR_SERVER_EXCESS)
        sys.exit(0)

    treble_path = 'C:\\dam' + 'g\\data\\high_frequency.json'
    if _HANDLE_DICT['packed_stat'] == 'yes':
        if not os.path.exists(treble_path):
            print(_ERROR_ACTION_HANDLE)
            sys.exit(0)

    record_home = 'C:\\dam' + 'g\\tmp'
    if os.path.exists(record_home):
        shutil.rmtree(record_home)

    # Get option values from configuration.
    cfm = ConfigManage()
    cfm.sector_name = 'public'
    cfm.option_name = 'start_time'
    string_time = cfm.reveal_normal(1)

    cfm.sector_name = 'oracle'
    cfm.option_name = 'sys_password'
    manage_code = cfm.reveal_normal(1)

    cfm.option_name = 'users'
    schema_info = cfm.reveal_normal(1)
    schema_info = schema_info.upper()
    schema_list = schema_info.split(',')

    # Set option values to configuration.
    cfm.option_name = 'degree_count'
    cfm.record_senior('0')

    cfm.option_name = 'degree_total'
    cfm.record_senior('0')

    # Make the argv information.
    option_dict = {}
    option_dict.update({'pwd': manage_code})
    option_dict.update({'usr': schema_list})
    option_dict.update({'day': string_time})
    option_dict.update({'out': _HANDLE_DICT['manual_stat']})
    log.debug(option_dict)

    # Start the child module.
    try:
        module_inst = dam_low_frequency.ModuleManage(option_dict)
        module_inst.obtain_object()

        module_inst = dam_show_object.ModuleManage(option_dict)
        module_inst.obtain_object()

        module_inst = dam_show_dml.ModuleManage(option_dict)
        module_inst.obtain_object()

        module_inst = dam_show_dql.ModuleManage(option_dict)
        module_inst.obtain_object()

        module_inst = dam_show_ddl.ModuleManage(option_dict)
        module_inst.obtain_object()

    except Exception as e:
        log.debug(e)
        print(_ERROR_ORACLE_EXCEPT)

        sys.exit(0)

    # Make the zip packet.
    if _HANDLE_DICT['packed_stat'] == 'yes':
        stm = SystemManage()
        stm.create_packet(schema_list)
        stm.encode_object()

    # Expire the high frequency record file.
    if os.path.exists(treble_path):
        os.remove(treble_path)

    if _HANDLE_DICT['manual_stat'] == 'yes':
        print('Job done.')

    return None


def disable_module():
    """
    Function to stop the collect module.
    :return:
    """
    # Delete cron plan.
    reduce_plan = 'sch' + 'tasks /delete /tn dam_high_single /f'
    os.system(reduce_plan)

    reduce_plan = 'sch' + 'tasks /delete /tn dam_high_series /f'
    os.system(reduce_plan)

    reduce_plan = 'sch' + 'tasks /delete /tn dam_collect /f'
    os.system(reduce_plan)

    return None


def except_module():
    """
    Function to stop the collect module.
    :return:
    """
    record_home = 'C:\\dam' + 'g\\data\\'

    # Delete cron plan.
    disable_module()

    # Clear the record files.
    while os.path.exists(record_home):
        try:
            shutil.rmtree(record_home)
        except PermissionError:
            time.sleep(1)
        else:
            break

    return None


def finish_module():
    """
    Function to finish the collect module.
    :return:
    """
    record_home = 'C:\\dam' + 'g\\data\\'
    record_path = 'C:\\dam' + 'g\\data\\high_frequency.json'

    # Check if all the information be collected.
    if not os.path.exists(record_path):
        print(_ERROR_ACTION_HANDLE)
        sys.exit(0)

    # Delete cron plan.
    disable_module()

    # Clear the record files.
    while os.path.exists(record_home):
        try:
            shutil.rmtree(record_home)
        except PermissionError:
            time.sleep(1)
        else:
            break

    return None


def status_module():
    """
    Function to get the collect module status information.
    :return:
    """
    cfm = ConfigManage()

    # Get option values from configuration.
    cfm.sector_name = 'oracle'
    cfm.option_name = 'users'
    schema_info = cfm.reveal_normal(1)
    schema_info = schema_info.upper()
    schema_list = schema_info.split(',')

    cfm.sector_name = 'public'
    cfm.option_name = 'cycle_time'
    circle_total = cfm.reveal_normal(1)

    cfm.option_name = 'cycle_count'
    circle_count = cfm.reveal_senior()

    cfm.option_name = 'degree_count'
    degree_count = int(cfm.reveal_senior())

    cfm.option_name = 'degree_total'
    degree_total = int(cfm.reveal_senior())

    # Ddl/dml/dql degree.
    for usr in schema_list:
        degree_total += 3
        if os.path.exists('C:\\dam'+'g\\data\\'+usr+'.ddl'):
            degree_count += 1
        if os.path.exists('C:\\dam'+'g\\data\\'+usr+'.dml'):
            degree_count += 1
        if os.path.exists('C:\\dam'+'g\\data\\'+usr+'.dql'):
            degree_count += 1

    # Get total/current collect number.
    # High frequency
    degree_total += 7
    degree_path = 'C:\\dam' + 'g\\data\\high_frequency.json'
    if os.path.exists(degree_path):
        degree_count += 7

    # Show information.
    degree_info = str(round(int(circle_count)*100/int(circle_total), 2))
    reduce_info = str(int(circle_total)-int(circle_count))
    return_info = 'Progress:\t' + degree_info + '%'
    return_info += '\tRemaining days: ' + reduce_info
    print(return_info)

    degree_info = str(round(degree_count*100/degree_total, 2))
    reduce_info = str(degree_total-degree_count)
    return_info = 'Integrity:\t' + degree_info + '%'
    return_info += '\tMissing ' + reduce_info + ' collect objects.'
    print(return_info)

    return None


if __name__ == '__main__':
    # Make the module logger function.
    lgm = LoggerManage()
    lgm.create_logger()

    # Receive the values by actions and options.
    parser_args = argparse.ArgumentParser()
    action_args = parser_args.add_subparsers()
    action_args.required = True

    action_head = action_args.add_parser('start')
    action_head.set_defaults(func=enable_module)

    action_plan = action_args.add_parser('plan')
    action_plan.set_defaults(func=timing_module)

    action_exec = action_args.add_parser('run')
    action_exec.set_defaults(func=layout_module)

    action_stop = action_args.add_parser('pause')
    action_stop.set_defaults(func=disable_module)

    action_abort = action_args.add_parser('abort')
    action_abort.set_defaults(func=except_module)

    action_tail = action_args.add_parser('finish')
    action_tail.set_defaults(func=finish_module)

    action_stat = action_args.add_parser('status')
    action_stat.set_defaults(func=status_module)

    # Call the functions to deal with the specified action.
    # Print help information if the action not exists.
    arg = parser_args.parse_args()
    arg.func()
