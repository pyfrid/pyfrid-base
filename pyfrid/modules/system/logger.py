#  Copyright 2012 Denis Korolkov
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

import collections
import logging
import traceback
import os
import sys

from logging import FileHandler
from logging import StreamHandler
from logging.handlers import SMTPHandler
from pyfrid.core.sysmod import _BaseSystemModule
from pyfrid.core.signal import Signal
from pyfrid.core.settings import StringSetting, IntSetting, BoolSetting

DEBUG_LEVEL=1
INFO_LEVEL=2
WARNING_LEVEL=3
ERROR_LEVEL=4
EXCEPTION_LEVEL=5
             
LOGFILEFORMAT="""
---
Time: %(asctime)s
Level: %(levelname)s
Path: %(pathname)s
Module: %(module)s
Function: %(funcName)s
Line: %(lineno)d
Object: %(object)s 
User: %(user)s
Message: %(message)s

"""

EMAILFORMAT="""
---
Time: %(asctime)s
Level: %(levelname)s
Object: %(object)s 
User: %(user)s
Message: %(message)s

"""

STREAMFORMAT="%(object)15s %(levelname)10s  %(message)s"
 
DATEFMT="%Y-%m-%d %H:%M:%S"
TIMEFMT="%H:%M:%S"

logging.addLevelName(DEBUG_LEVEL,"DEBUG")
logging.addLevelName(INFO_LEVEL,"INFO")
logging.addLevelName(WARNING_LEVEL,"WARNING")
logging.addLevelName(ERROR_LEVEL,"ERROR")
logging.addLevelName(EXCEPTION_LEVEL,"EXCEPTION")

class PyfridSMTPHandler(SMTPHandler):
    
    def __init__(self,mailhost,fromaddr,toaddrs,subject,credentials=None,secure=False):
        SMTPHandler.__init__(self,mailhost,fromaddr,toaddrs,subject,credentials)
        self.secure=secure
    
    def emit(self, record):
        try:
            import smtplib
            import string # for tls add this line
            try:
                from email.utils import formatdate
            except ImportError:
                formatdate = self.date_time
            port = self.mailport
            if not port:
                port = smtplib.SMTP_PORT
            smtp = smtplib.SMTP(self.mailhost, port)
            msg = self.format(record)
            msg = "From: %s\r\nTo: %s\r\nSubject: %s\r\nDate: %s\r\n\r\n%s" % (
                                                                                self.fromaddr,
                                                                                string.join(self.toaddrs, ","),
                                                                                self.getSubject(record),
                                                                                formatdate(), msg)
            if self.username:
                if self.secure:
                    smtp.ehlo() # for tls add this line
                    smtp.starttls() # for tls add this line
                    smtp.ehlo() # for tls add this line
                smtp.login(self.username, self.password)
            smtp.sendmail(self.fromaddr, self.toaddrs, msg)
            smtp.quit()
        except (KeyboardInterrupt, SystemExit):
            raise
        except:
            self.handleError(record)        
        
class MemoryHandler(logging.Handler):
    
    def __init__(self,maxlen,level):
        logging.Handler.__init__(self)
        self.setLevel(level)
        self._buffer=collections.deque(maxlen=maxlen)
        
    def emit(self, record):
        # Insert log record:
        self._buffer.append({"time":record.created,
                             "level":record.levelname,
                             "object":record.object,
                             "user":record.user,
                             "message":record.msg
                            })
                    
    def get_messages(self):
        return list(self._buffer)   

class PyfridLogger(logging.Logger):
    
    def __init__(self, module, *args, **kwargs): 
        logging.Logger.__init__(self, *args, **kwargs)
        self._module=module
        self._info_count=0
        self._warning_count=0
        self._error_count=0
        self._exception_count=0
    
    def num_info(self):
        return self._info_count
    
    def num_warnings(self):
        return self._warning_count
    
    def num_error(self):
        return self._error_count
    
    def num_exception(self):
        return self._exception_count
    
    def makeRecord(self, name, lvl, fn, lno, msg, args, exc_info, func=None, extra=None):
        rv = logging.Logger.makeRecord(self, name, lvl, fn, lno, msg, args, exc_info, func, extra)
        if  lvl==INFO_LEVEL:
            self._info_count+=1
            self._module.info_record_signal(rv)
            return rv
        elif lvl==WARNING_LEVEL:
            self._warning_count+=1
            self._module.warning_record_signal(rv)
            return rv
        elif lvl==ERROR_LEVEL:
            self._error_count+=1
            self._module.error_record_signal(rv)
            return rv
        elif lvl==EXCEPTION_LEVEL:
            self._exception_count+=1
            self._module.exception_record_signal(rv)
            return rv
        elif  lvl==DEBUG_LEVEL:
            self._module.debug_record_signal(rv)
            return rv
        return rv
    
    def clear_counters(self):
        self._info_count=0
        self._warning_count=0
        self._error_count=0
        self._exception_count=0
                            
class BaseLoggerModule(_BaseSystemModule):
        """
        This is base logger module, system module which manages logging messages of your application.
        It is based on the standard python logging module, where log messages are emitted by handlers.
        PyFRID logger supports by default logging to stdout, file and email. 
        """
        logfile_format=LOGFILEFORMAT
        email_format=EMAILFORMAT
        stream_format=STREAMFORMAT
        memory_bufsize = 50
        
        #: string setting for the smtp host. It is used for the logging to email.
        smtp_host   = StringSetting   ("",  fixed=True)
         
        #: integer setting for the smtp port.
        smtp_port   = IntSetting      (587, fixed=True)
        
        #: string setting for the smtp user.
        smtp_user   = StringSetting   ("",  fixed=True)
        
        #: string setting for the smtp password.
        smtp_pass   = StringSetting   ("",  fixed=True)
        
        #: string setting for the smtp secure type.
        smtp_secure = StringSetting   ("",  fixed=True)
        
        #: string setting for the *from* email.
        smtp_from = StringSetting   ("",  fixed=True)
        
        def __init__(self, *args, **kwargs):
            self._strh=None
            self._lgfh=None
            self._emailh=None
            
            self._level=INFO_LEVEL
            
            self._logger=PyfridLogger(self, "pyfrid")
            
            self._memory_handler=MemoryHandler(max(self.memory_bufsize, 1), self._level)
            self._logger.addHandler(self._memory_handler)
            
            self._current_user=None
        
            self.debug_record_signal=Signal(self)
            self.info_record_signal=Signal(self)
            self.warning_record_signal=Signal(self)
            self.error_record_signal=Signal(self)
            self.exception_record_signal=Signal(self)
            
            super(BaseLoggerModule, self).__init__(*args, **kwargs)
            
            self.debug_signal.connect(self.debug_slot)
            self.info_signal.connect(self.info_slot)
            self.warning_signal.connect(self.warning_slot)
            self.error_signal.connect(self.error_slot)
            self.exception_signal.connect(self.exception_slot)
                
        def set_logdir(self, directory):
            logdir=os.path.join(self.app.projpath,"log")
            if directory: logdir=directory
            if not os.path.exists(logdir):
                os.makedirs(logdir)
            return logdir
        
        def set_log2file(self, val):
            if val:
                self._lgfh=self.add_logfile_handler(os.path.join(self.logdir, "{0}.log".format(self.app.projname)), self._lgfh)
            else:
                self.remove_handler(self._lgfh)
                self._lgfh=None
            return val
        
        def set_log2stdout(self, val):
            if val:
                self._strh=self.add_stream_handler(sys.stdout, self._strh)
            else:
                self.remove_handler(self._strh)
                self._strh=None
            return val
        
        def set_log2email(self, val):
            if val:
                self._emailh=self.add_smtp_handler(self._current_user, self._emailh)
            else:
                self.remove_handler(self._emailh)
                self._emailh=None
            return val
        
        def set_debugmode(self, val):
            if val:
                self._level=DEBUG_LEVEL
            else:
                self._level=INFO_LEVEL
            self._memory_handler.setLevel(self._level)
            return val
            
        def set_current_user(self, user, **kwargs):
            if user!=None:
                self._current_user=user
                if self.email_log:
                    self.add_smtp_handler(self._current_user, self._emailh) 
                     
        def add_stream_handler(self, stream, oldhandler=None):
            try:
                self.remove_handler(oldhandler)
                formatter = logging.Formatter(self.stream_format, TIMEFMT)
                handler=StreamHandler(stream)
                handler.setLevel(self._level)
                handler.setFormatter(formatter)
                self._logger.addHandler(handler)
                return handler
            except Exception:
                self.exception("Cannot add stream handler")
                
        def add_smtp_handler(self,user,oldhandler=None):
            try:
                self.remove_handler(oldhandler)
                user_email=user.email
                if user_email and self.smtp_from:
                    formatter = logging.Formatter(self.email_format, DATEFMT)
                    handler=PyfridSMTPHandler(self._smtp_host, self.email_from, user_email,
                                        "PYFRID",self._smtp_user,secure=self._smtp_secure)
                    handler.setLevel(ERROR_LEVEL)
                    handler.setFormatter(formatter)
                    self._logger.addHandler(handler)
                    return handler
                return None
            except Exception:
                self.exception("Cannot add smtp handler")
        
        def add_logfile_handler(self,filename,oldhandler=None):
            try:
                self.remove_handler(oldhandler) 
                formatter = logging.Formatter(self.logfile_format, DATEFMT)
                handler=FileHandler(filename)
                handler.setLevel(self._level)
                handler.setFormatter(formatter)    
                self._logger.addHandler(handler)
                return handler
            except Exception:
                self.exception("Cannot add logfile '{0}'".format(filename))
                
        def remove_handler(self,handler):
            if handler!=None:
                try:
                    self._logger.removeHandler(handler)
                except Exception, err:
                    self.exception("Problem while removing handler: \n{0}".format(err))
        
        def _log_slot(self, msg, level, exc_info=False, **kwargs):
            objname=getattr(kwargs["sender"],"name","")
            user=self._current_user.login if self._current_user!=None else ""
            self._logger.log(level,str(msg),exc_info=exc_info, extra={'object':objname,'user':user})
        
        def debug_slot(self,msg,**kwargs):
            try:
                self._log_slot(msg, DEBUG_LEVEL, **kwargs)
            except Exception:
                traceback.print_exc()
        
        def info_slot(self,msg,**kwargs):
            try:
                self._log_slot(msg, INFO_LEVEL, **kwargs)
            except Exception:
                traceback.print_exc()
    
        def warning_slot(self,msg,**kwargs):
            try:
                self._log_slot(msg, WARNING_LEVEL, **kwargs)
            except Exception:
                traceback.print_exc()
    
        def error_slot(self,msg,**kwargs):
            try:
                self._log_slot(msg, ERROR_LEVEL, **kwargs)
            except Exception:
                traceback.print_exc()
           
        def exception_slot(self,msg,**kwargs):
            try:
                self._log_slot(msg, EXCEPTION_LEVEL, exc_info=True, **kwargs)
            except Exception:
                traceback.print_exc()
                          
        def get_messages(self):
            return self._memory_handler.get_messages()
        
        def release(self):
            self._logger.clear_counters()
        
        def status(self):
            return (
                    ("Errors",     self._logger.num_error(),''    ),
                    ("Warnings",   self._logger.num_warnings(),''  ),
                    ("Messages",   self._logger.num_info(),''     ),
                    ("Exceptions", self._logger.num_exception(),'')
                   )                 
        
        #: boolean fixed setting for switching on/off debugging mode
        debugmode  = BoolSetting   (False, setter=set_debugmode,  fixed=True )
        
        #: string fixed setting for the path to a directory with log file
        logdir     = StringSetting ("",    setter=set_logdir,     fixed=True )
        
        #: boolean fixed setting for switching on/off logging to standard output 
        stdout_log = BoolSetting   (True,  setter=set_log2stdout, fixed=True )
        
        #: boolean fixed setting for switching on/off logging to a log file
        file_log   = BoolSetting   (True,  setter=set_log2file,   fixed=True )
        
        #: boolean fixed setting for switching on/off logging to email of a current user
        email_log  = BoolSetting   (True,  setter=set_log2email,  fixed=True )
        
