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

import abc
import datetime
import time
from pyfrid.core.sysmod import BaseSystemModule
from pyfrid.core.settings import BoolSetting
from pyfrid.core.descriptor import use_module
from pyfrid.core.signal import Signal

class ParseError(Exception):pass
class ValidateError(Exception):pass
class ExecuteError(Exception):pass

class BaseVMModule(BaseSystemModule):
    """
    This is base class of a virtual machine module. It has basic functionality and
    defines few abstract methods, which must be implemented in subclasses.
    """
    auth_module=use_module("authentication")
    
    def __init__(self, *args, **kwargs):
        """
        The default implementation of virtual machine has the following signals:
        
        * before_execute_signal
        * after_execute_signal
        * before_validate_signal
        * after_validate_signal
        
        """
        super(BaseVMModule,self).__init__(*args, **kwargs)
        self._current_macro=''
        self._current_line=''
        self._runtime=None
        self._started=None
        
        self._busy=False
                
        self.before_execute_signal=Signal(self)
        self.after_execute_signal=Signal(self)
        self.before_validate_signal=Signal(self)
        self.after_validate_signal=Signal(self)

    @property    
    def busy(self):
        """Returns True if there is a running command."""
        return self._busy   

    @property
    def current_macro(self):
        """Returns a filename of a currently running macro."""
        return self._current_macro
    
    @property
    def current_line(self):
        """Returns a current line of a macro."""
        return self._current_line
    
    @property
    def runtime(self):
        """Returns an estimated running time of a command or a macro."""
        if self._runtime!=None:
            return datetime.timedelta(seconds=self._runtime)
        return ''
    
    @property
    def started(self):
        """Returns time stamp when a macro or a command was started."""
        if self._started!=None:
            return time.strftime("%d %b %H:%M:%S", time.localtime(self._started))
        return ''
    
    @property
    def finishes(self):
        """Returns an estimated time when a currently running command or macro will be finished."""
        if self._started!=None and self._runtime!=None:
            return time.strftime("%d %b %H:%M:%S", time.localtime(self._started+self._runtime))
        return ''

    @property
    def elapsed(self):
        """Returns an estimated elapsed time."""
        if self._started!=None and self.busy:
            return datetime.timedelta(seconds=time.time()-self._started)
        return ''

    def set_excstop(self,val):
        if val: self.logger_module.exception_record_signal.connect(self.stop_slot)
        else: self.logger_module.exception_record_signal.disconnect(self.stop_slot)
        return val

    def set_errstop(self,val):
        if val: self.logger_module.error_record_signal.connect(self.stop_slot)
        else: self.logger_module.error_record_signal.disconnect(self.stop_slot)
        return val

    def stop_slot(self, *args, **kwargs):
        self.call_stop()
    
    @abc.abstractmethod
    def parse_code(self, code):
        """Abstract method which parses a code."""
        return None

    @abc.abstractmethod
    def validate_ast(self, ast):
        """Abstract method which validates a code and returns its estimated runtime, normally after parsing it."""
        return 0.0
    
    @abc.abstractmethod
    def execute_ast(self, ast):
        """Abstract method which executes a code, normally after parsing and validation."""
        pass
           
    def execute_code(self, code):
        """
        Main method, which performs execution of a code. Before execution the signal *before_execute_signal*
        is emitted. If parsing and validation of a code were successful, this function starts execution of a AST.
        """
        self._busy=True
        try:
            self.before_execute_signal()
            ast=self.parse_code(code)
            self._runtime=self.validate_ast(ast)
            self.info("Estimated runtime: {0}".format(self.runtime))
            self._started=time.time()
            self.execute_ast(ast)
        except ParseError, err:
            self.error("Parse error: {0}".format(err))
            return 
        except ValidateError, err:
            self.error("Validation error: {0}".format(err))
            return 
        except ExecuteError, err:
            self.error("Execution error: {0}".format(err))
            return 
        finally:
            self.after_execute_signal()
            self._busy=False
        self._runtime=None
        self._started=None
        self._current_line=''
        self._current_macro='' 
            
    def validate_code(self, code):
        """Method for a code validation."""
        self._busy=True
        try:
            self.before_validate_signal()
            ast=self.parse_code(code)
            self._runtime=self.validate_ast(ast)
            self._started=time.time()
        except ParseError, err:
            self.error("Parse error: {0}".format(err))
            return
        except ValidateError, err:
            self.error("Validation error: {0}".format(err))
            return
        finally:
            self.after_validate_signal()
            self._busy=False
        self._current_line=''
        self._current_macro=''                
    
    def get_device(self,name,permission=""):
        obj=self.app.device_manager.get_object_byname(name,exc=True)
        if permission and not self.auth_module.validate_access(obj,permission):
            ParseError("Access denied. No '{0}' permission for the object '{1}'".format(permission,obj.name))
        return obj
    
    def get_command(self,name,permission=""):
        obj=self.app.command_manager.get_object_byname(name,exc=True)
        if permission and not self.auth_module.validate_access(obj,permission):
            raise ParseError("Access denied. No '{0}' permission for the object '{1}'".format(permission,obj.name))
        return obj

    def get_module(self,name,permission=""):
        obj=self.app.module_manager.get_object_byname(name,exc=True)
        if permission and not self.auth_module.validate_access(obj,permission):
            raise ParseError("Access denied. No '{0}' permission for the object '{1}'".format(permission,obj.name))
        return obj
    
    def get_sysmod(self,name,permission=""):
        obj=self.app.system_manager.get_object_byname(name,exc=True)
        if permission and not self.auth_module.validate_access(obj,permission):
            raise ParseError("Access denied. No '{0}' permission for the object '{1}'".format(permission,obj.name))
        return obj

    def status(self):
        """Status handler of this module. It returns a current running filename, current line, 
        time when a command was started, estimated runtime, elapsed time and time when current command 
        will finish."""
        return (
                ("Macro",   self.current_macro, ""),
                ("Line",    self.current_line, ""),
                ("Started", self.started, ""),
                ("Runtime", self.runtime, ""),
                ("Elapsed", self.elapsed, ""),
                ("Finishes", self.finishes, ""),
               )
    
    #: boolean setting which indicates whether to stop execution of a command or a macro 
    #: when exception was emitted    
    exc_stop=BoolSetting(True, setter=set_excstop, fixed=True)
    
    #: boolean setting which indicates whether to stop execution of a command or a macro 
    #: when error was emitted
    err_stop=BoolSetting(True, setter=set_errstop, fixed=True)
    