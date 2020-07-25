import configparser
import json
import logging
import os
import stat
import subprocess

_LOGGER_INST = None
_MANUAL_STAT = 'yes'
_COLLECT_MAX = 0
_COLLECT_NUM = 0


def record_degree():
    """
    Function to record max/current collect object number.
    :return:
    """
    config_path = '/etc/dam' + 'g.conf'

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
            fip.writelines('set lines 1024;\n')
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
    oracle_user = ''
    oracle_home = ''
    logger_inst = None

    def __init__(self, oracle_user, oracle_home):
        self.oracle_user = oracle_user
        self.oracle_home = oracle_home
        self.logger_inst = _LOGGER_INST

    def obtain_object(self):
        """
        Method to get object relationship.
        :return:                    object relationship list
        """
        log = self.logger_inst

        # Make the shell script path.
        script_name = '.list_obj.sh'
        script_path = self.oracle_home + script_name

        # Create and edit the shell script.
        shm = ScriptManage(script_path)
        shm.create_script()

        manage_info = 'select name,type,referenced_owner,' \
                      'referenced_name,referenced_type' \
                      ' from dba_dependencies where owner=\'{user}\';' \
            .format(user=self.oracle_user)
        shm.modify_script(manage_info)

        # Run the shell script by oracle user.
        handle_path = 'su - oracle -c \'{path}\''\
            .format(path=script_path)
        handle_path += ' |awk \'{print$1\"|||\"$2\"' \
                       '|||\"$3\"|||\"$4\"|||\"$5}\''

        try:
            pip = subprocess.Popen(args=handle_path,
                                   shell=True,
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.STDOUT)
        except Exception as e:
            if log:
                log.debug(e)
            return None
        else:
            pip.wait()
            return_info = pip.stdout.readlines()

        # Delete the tmp script.
        shm.delete_script()

        return return_info

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
        script_name = '.list_obj_index.sh'
        script_path = self.oracle_home + script_name

        # Create and edit the shell script.
        shm = ScriptManage(script_path)
        shm.create_script()

        manage_info = 'select table_name||\'|\'||index_name||\'|\'' \
                      '||to_char(wm_concat(column_name)) as column_list' \
                      ' from dba_ind_columns where index_owner=\'{user}\'' \
                      ' group by table_name, index_name;'\
            .format(user=self.oracle_user)
        shm.modify_script(manage_info)

        # Run the shell script by oracle user.
        handle_path = 'su - oracle -c \'{path}\''\
            .format(path=script_path)

        try:
            pip = subprocess.Popen(args=handle_path,
                                   shell=True,
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.STDOUT)
        except Exception as e:
            if log:
                log.debug(e)
            return None
        else:
            return_info = pip.stdout.readlines()

        if return_info:
            _COLLECT_NUM += 1

        # Delete the tmp script.
        shm.delete_script()

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
        script_name = '.list_obj_lob.sh'
        script_path = self.oracle_home + script_name

        # Create and edit the shell script.
        shm = ScriptManage(script_path)
        shm.create_script()

        manage_info = 'select table_name||\'|\'||column_name||\'|\'||' \
                      'segment_name||\'|\'||tablespace_name from' \
                      ' dba_lobs where owner=\'{user}\';'\
            .format(user=self.oracle_user)
        shm.modify_script(manage_info)

        # Run the shell script by oracle user.
        handle_path = 'su - oracle -c \'{path}\''\
            .format(path=script_path)

        try:
            pip = subprocess.Popen(args=handle_path,
                                   shell=True,
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.STDOUT)
        except Exception as e:
            if log:
                log.debug(e)
            return None
        else:
            return_info = pip.stdout.readlines()

        if return_info:
            _COLLECT_NUM += 1

        # Delete the tmp script.
        shm.delete_script()

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
        script_name = '.list_obj_trigger.sh'
        script_path = self.oracle_home + script_name

        # Create and edit the shell script.
        shm = ScriptManage(script_path)
        shm.create_script()

        manage_info = 'select table_name||\'|\'||trigger_name||\'|\'||' \
                      'to_char(wm_concat(column_name)) as column_list' \
                      ' from dba_trigger_cols where trigger_owner=\'{user}\'' \
                      ' group by table_name, trigger_name;'\
            .format(user=self.oracle_user)
        shm.modify_script(manage_info)

        # Run the shell script by oracle user.
        handle_path = 'su - oracle -c \'{path}\''\
            .format(path=script_path)

        try:
            pip = subprocess.Popen(args=handle_path,
                                   shell=True,
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.STDOUT)
        except Exception as e:
            if log:
                log.debug(e)
            return None
        else:
            return_info = pip.stdout.readlines()

        if return_info:
            _COLLECT_NUM += 1

        # Delete the tmp script.
        shm.delete_script()

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
        script_name = '.list_obj_view.sh'
        script_path = self.oracle_home + script_name

        # Create and edit the shell script.
        shm = ScriptManage(script_path)
        shm.create_script()

        manage_info = 'select name||\'|\'||referenced_name' \
                      '||\'|\'||referenced_type from dba_dependencies' \
                      ' where owner=\'{user}\' and TYPE=\'VIEW\';'\
            .format(user=self.oracle_user)
        shm.modify_script(manage_info)

        # Run the shell script by oracle user.
        handle_path = 'su - oracle -c \'{path}\''\
            .format(path=script_path)

        try:
            pip = subprocess.Popen(args=handle_path,
                                   shell=True,
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.STDOUT)
        except Exception as e:
            if log:
                log.debug(e)
            return None
        else:
            return_info = pip.stdout.readlines()

        if return_info:
            _COLLECT_NUM += 1

        # Delete the tmp script.
        shm.delete_script()

        return return_info


class ModuleManage(object):
    """
    Class about module operations.
    :method obtain_object:
    """
    oracle_user = []
    oracle_home = ''
    record_path = 'object_relation.json'

    def __init__(self, option_dict):
        self.oracle_user = option_dict['usr']

        if option_dict['pwd'][-1] != '/':
            self.oracle_home = option_dict['pwd'] + '/'
        else:
            self.oracle_home = option_dict['pwd']

        record_home = '/root/DAM' + 'G/'
        if not os.path.exists(record_home):
            os.makedirs(record_home)
        self.record_path = record_home + 'object_relation.json'

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
        schema_list = []

        # Make the module logger function.
        lgm = LoggerManage()
        lgm.create_logger()

        for usr in oracle_user:
            usr = usr.upper()

            # Get oracle object information.
            ocm = OracleManage(oracle_home=oracle_home,
                               oracle_user=usr)

            # Get index information.
            if _MANUAL_STAT == 'yes':
                print('Collecting information about index object ...')

            return_list = ocm.obtain_index()

            object_inst = {}
            object_list = []
            for i in return_list:
                single_info = i.decode('UTF-8').rstrip()

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

            object_inst = {}
            object_list = []
            for i in return_list:
                single_info = i.decode('UTF-8').rstrip()

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

            object_inst = {}
            object_list = []
            for i in return_list:
                single_info = i.decode('UTF-8').rstrip()

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

            object_inst = {}
            object_list = []
            for i in return_list:
                single_info = i.decode('UTF-8').rstrip()

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
        with open(self.record_path, 'w') as fip:
            fip.writelines(str(object_json))

        # Record degree information.
        record_degree()

        return None


if __name__ == '__main__':
    mmm = ModuleManage({'usr': ['SYS'],
                        'pwd': '/home/oracle',
                        'out': 'yes'})
    mmm.obtain_object()
