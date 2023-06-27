import inspect
import json
from pathlib import Path
import requests
import socket
import datetime
from string import Template


class LoggerException(Exception):
    pass


class Logger():
    config = dict()
    log_config_file = "log_config.json"
    fmt = "$log_level|$date_time|$app_id|$host_name|$message|$file|$module"
    err_fmt = "$log_level|$date_time|$app_id|$host_name|$message|$file|$module|$line|$error"
    log_levels = {"ERROR" : 4, "WARNING" : 3, "INFO" : 2, "DEBUG" : 1}
    log_msg_empty = "Log message is empty"

    def __init__(self):

        '''Check if config file exists, and get config data'''

        if ( Path(self.log_config_file).is_file() ):
            with open(self.log_config_file) as config_file:
                self.config = json.load(config_file)
        else:
            self.__basic_configure()

    def __basic_configure(self, db_storage=False, log_level="WARNING"):

        '''Create default config file'''

        self.config["db_storage"] = db_storage
        self.config["log_level"] = log_level
        with open(self.log_config_file, 'w') as f:
            f.write(json.dumps(self.config, indent=4))

    def configure(self, app_id, db_storage=None, log_level=None, url=None):

        '''Update config file'''

        if ( not app_id or not str.isdigit(str(app_id)) ):
            raise LoggerException("A valid application ID must be provided")

        if ( url == None ):
            raise LoggerException("A valid URL must be provided")
        else:
            resp = requests.get(url)
            if ( resp.status_code != 200 ):
                raise LoggerException("A valid URL must be provided")

        self.url = url
        self.config["url"] = url
        self.config["app_id"] = app_id if ( app_id ) else self.config["app_id"]
        self.config["db_storage"] = db_storage if ( db_storage ) else self.config["db_storage"]
        self.config["log_level"] = log_level if ( log_level ) else self.config["log_level"]
        with open(self.log_config_file, 'w') as f:
                f.write(json.dumps(self.config, indent=4))


    def get_hostname(self):
        return socket.gethostname()
    

    def get_datetime(self):
        return str(datetime.datetime.now())


    def get_error_fields(self, s):

        '''Get the file name, module name, line no and error from the traceback'''

        d = dict()
        lst = s.strip().split('\n')
        t = lst[1].strip().split(', ')
        d["file"] = t[0].split(' ', 1)[1].replace('"', '').replace('<','').replace('>', '').strip()
        d["module"] = t[2].split(' ')[1].replace('<','').replace('>', '').strip()
        d["line"] = t[1].split(' ')[1].strip()
        d["error"] = lst[-1].strip()
        return d


    def get_req_fields(self):
        fields = dict()
        fields["date_time"] = self.get_datetime()
        fields['app_id'] = str(self.config['app_id'])
        fields['host_name'] = self.get_hostname()
        return fields


    def get_formatted_str(self, msg):
        return {
            "message" : Template(self.fmt).substitute(msg)
        }
    

    def get_err_formatted_str(self, msg):
        return {
            "message" : Template(self.err_fmt).substitute(msg)
        }
    

    def debug(self, message=None):
        if ( message == None ):
            raise LoggerException(self.log_msg_empty)
        self.__log(message, "DEBUG")
        return 1


    def info(self, message=None):
        if ( message == None ):
            raise LoggerException(self.log_msg_empty)
        self.__log(message, "INFO")
        return 1


    def warning(self, message=None):
        if ( message == None ):
            raise LoggerException(self.log_msg_empty)
        self.__log(message, "WARNING")
        return 1


    def __log(self, message, log_level):

        '''Creates payload with required fields and send request to microservice'''

        if ( self.log_levels[log_level] < self.log_levels[self.config["log_level"]] ):
            return
        if ( message == None ):
            raise LoggerException(self.log_msg_empty)
        
        fields = self.get_req_fields()
        frame = inspect.stack()[1]
        fields['message'] = message
        fields["log_level"] = log_level
        fields["file"] = frame.filename
        fields["module"] = frame.function

        payload = self.get_formatted_str(fields)
        print()
        self.__send_log_to_file(payload)
        if ( self.config["db_storage"] ):
            self.__send_log_to_db(fields)
        


    def error(self, message=None, exception=None):

        '''Creates payload with required fields and send request to microservice'''

        if ( message == None ):
            raise LoggerException(self.log_msg_empty)
        if ( exception == None ):
            raise LoggerException("Exception is missing")
        
        fields = dict()
        tmp = self.get_error_fields(exception)
        frame = inspect.stack()[1]
        fields['message'] = message
        fields["log_level"] = "ERROR"
        fields["file"] = frame.filename
        fields["line"] = tmp["line"]
        fields["error"] = tmp["error"]
        fields["module"] = frame.function
        fields.update(self.get_req_fields())

        payload = self.get_err_formatted_str(fields)
        self.__send_log_error_to_file(payload)
        if ( self.config["db_storage"] ):
            self.__send_log_error_to_db(fields)
        return 1


    def __send_log_to_file(self, log):
        self.__send_log_request(self.url + '/logfile', log)


    def __send_log_to_db(self, fields):
        self.__send_log_request(self.url + '/logdb', fields)


    def __send_log_error_to_file(self, log):
        self.__send_log_request(self.url + '/logerrorfile', log)


    def __send_log_error_to_db(self, fields):
        self.__send_log_request(self.url + '/logerrordb', fields)

        
    def __send_log_request(self, url, payload):
        try:
            requests.post(url, json=payload)
        except requests.exceptions.ConnectionError as e: 
            raise SystemExit(e)
        except requests.exceptions.RequestException as e: 
            raise SystemExit(e)
