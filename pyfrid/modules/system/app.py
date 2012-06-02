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

import traceback
from pyfrid.core.settings import StringSetting
from pyfrid.utils.threadpool import ThreadPool
from pyfrid.core.sysmod import BaseSystemModule
from pyfrid.core.descriptor import use_module
from pyfrid.core.device import device_registry
from pyfrid.core.command import command_registry
from pyfrid.core.module import module_registry
from pyfrid.core.command import get_completions

def connect_to_logger(logger_module, obj):
    obj.debug_signal.connect(logger_module.debug_slot)
    obj.info_signal.connect(logger_module.info_slot)
    obj.warning_signal.connect(logger_module.warning_slot)
    obj.error_signal.connect(logger_module.error_slot)
    obj.exception_signal.connect(logger_module.exception_slot)
       
class BaseApplicationModule(BaseSystemModule):
    """
    This is base class for application module. The application module is a system module which
    manages devices, commands and modules of your application, executes and validates the code by
    using *virtual_machine* system module, control permissions to objects using *authentication* module.
    It also has useful tools for developers to iterate over objects of different types.  
    """
    
    auth_module=use_module("authentication")
    vm_module=use_module("virtual_machine")

    instrument  = StringSetting("", fixed=True)
    responsible = StringSetting("", fixed=True)
    email       = StringSetting("", fixed=True)

    def __init__(self, *args, **kwargs):
        """Initializes application module, creates devices, modules and commands of application and connects
        their logging signals to the proper slots of the *logger* module 
        """
        super(BaseApplicationModule, self).__init__(*args,**kwargs)
        
        self._execpool=ThreadPool(self, num_threads=2, persist=True, queue_size=1)
        self._stoppool=ThreadPool(self, num_threads=1, persist=True, queue_size=1)
        
        for alias, permissions, settings in self.app.config_manager.iterate_devices():
            obj=self.app.device_manager.create_object(device_registry[alias], self, permissions, settings)
            connect_to_logger(self.logger_module, obj)
        
        for alias, permissions, settings in self.app.config_manager.iterate_modules():
            obj=self.app.module_manager.create_object(module_registry[alias], self, permissions, settings)
            connect_to_logger(self.logger_module, obj)
        
        for alias, permissions, settings in self.app.config_manager.iterate_commands():
            obj=self.app.command_manager.create_object(command_registry[alias], self, permissions, settings)
            connect_to_logger(self.logger_module, obj)
                
                      
    def initialize(self):
        """Initialization handler. It iterates over all devices, modules and commands and calls *initialize* handler of each object.""" 
        for _, obj in self.iterate_devices():
            obj.call_initialize()
        for _,obj  in self.iterate_modules():
            obj.call_initialize()
        for _, obj in self.iterate_commands():
            obj.call_initialize()
        
    def shutdown(self):
        """Shutdown handler. It iterates over all devices, modules and commands and calls *shutdown* handler of each object."""
        for _, obj in self.iterate_commands():
            obj.call_shutdown()
        for _, obj  in self.iterate_modules():
            obj.call_shutdown()
        for _, obj in self.iterate_devices():
            obj.call_shutdown()
            
    def stop(self):
        """
        Shutdown handler. It iterates over all devices, modules and commands and calls *stop* handler of each object.
        Stopping is performed in another thread in order to avoid any blocking of the main thread of application.
        """
        def task(app):
            app.info("Stop all objects...")
            self.vm_module.call_stop()
            for _,obj in app.iterate_commands():
                obj.call_stop()
            for _,obj in app.iterate_modules():
                obj.call_stop()
            for _,obj in app.iterate_devices():
                obj.call_stop()
        self._execpool.add_task(task, self)  

    def release(self):
        """Release handler. It iterates over all devices, modules and commands and calls *release* handler of each object.
        This handler is executed before running a command or a code."""
        for _, obj in self.iterate_commands():
            obj.call_release()
        for _,obj  in self.iterate_modules():
            obj.call_release()
        for _, obj in self.iterate_devices():
            obj.call_release()
            
    def login(self, login, password):
        """Calls function of the same name of *authentication* module."""
        return self.auth_module.login(login, password)
    
    def logout(self, login, password):
        """Calls function of the same name of *authentication* module."""
        return self.auth_module.logout(login, password)
    
    def execute_code(self, code):
        """Executes a code in another thread. Before execution every system module including *application* module is released."""
        if self.busy:
            self.warning("Can not execute command. Virtual machine is busy...")
            return
        if code:
            def task(app, code):
                app.info("Executing command: {0}".format(code))
                for _, obj in app.app.system_manager.iterate_objects():
                    obj.call_release()
                app.vm_module.execute_code(code)
            self._execpool.add_task(task, self, code)
        
    def validate_code(self, code):
        """Validates a code in another thread."""
        if self.busy:
            self.warning("Can not validate command. Virtual machine is busy...")
            return
        if code:
            def task(app, code):
                app.info("Validating command: {0}".format(code))
                for _, obj in app.app.system_manager.iterate_objects():
                    obj.call_release()
                app.vm_module.validate_code(code)
            self._execpool.add_task(task, self, code)
    
    @property
    def busy(self):
        """Calls property of the same name of *virtual_machine* module."""
        return self.vm_module.busy
    
    def validate_access(self, obj, permission):
        """Validates access to an object by checking object's permission."""
        return self.auth_module.validate_access(obj,permission)
        
    def iterate_devices(self, permission="", byname=False):
        """
        Iterator over devices in application. It yields a tuple *(name, reference)* for every device
        depending on permissions (if given). If argument *byname* is False this iterator will return device *alias*.
        """
        for name, obj in self.app.device_manager.iterate_objects(byname):
            if permission and not self.validate_access(obj,permission):
                continue
            yield(name, obj)
            
    def iterate_commands(self, permission="", byname=False):
        """
        Iterator over commands in application. It yields a tuple *(name, reference)* for every command
        depending on permissions (if given). If argument *byname* is False this iterator will return command *alias*.
        """
        for name, obj in self.app.command_manager.iterate_objects(byname):
            if permission and not self.validate_access(obj,permission):
                continue
            yield(name, obj)
                
    def iterate_modules(self, permission="", byname=False):
        """
        Iterator over modules presented in application. It yields a tuple *(name, reference)* for every module
        depending on permissions (if given). If argument *byname* is False this iterator will return module *alias*.
        """
        for name, obj in self.app.module_manager.iterate_objects(byname):
            if permission and not self.validate_access(obj,permission):
                continue
            yield(name, obj)
    
    def iterate_sysmods(self, permission="", byname=False):
        """
        Iterator over system modules presented in application. It yields a tuple *(name, reference)* for every module
        depending on permissions (if given). If argument *byname* is False this iterator will return module *alias*.
        """
        for name, obj in self.app.system_manager.iterate_objects(byname):
            if permission and not self.validate_access(obj, permission):
                continue
            yield(name, obj)
            
    def iterate_objects(self, permission="", byname=False):
        """
        Iterator over devices, commands and modules presented in application.
        It yields a tuple *(name, reference)* for every object depending on permissions (if given).
        If argument *byname* is False this iterator will return object *alias*.
        """
        for name, obj in self.iterate_devices  (permission, byname):
            yield (name, obj)
        for name, obj in self.iterate_commands (permission, byname):
            yield (name, obj)
        for name, obj in self.iterate_modules  (permission, byname):
            yield (name, obj)
        
    def get_device(self, name, permission="", byname=False, exc=False):
        """
        Returns device presented in application by its name or alias depending on permissions (if given).
        if *exc* is True the exception will be raised if device was not found.
        """
        if byname:
            obj=self.app.device_manager.get_object_byname(name,exc)
        else:
            obj=self.app.device_manager.get_object_byalias(name,exc)
        if obj!=None and permission and not self.validate_access(obj,permission):
            return None
        return obj
    
    def get_command(self,name,permission="",byname=False,exc=False):
        """
        Returns command presented in application by its name or alias depending on permissions (if given).
        if *exc* is True the exception will be raised if command was not found.
        """
        if byname:
            obj=self.app.command_manager.get_object_byname(name,exc)
        else:
            obj=self.app.command_manager.get_object_byalias(name,exc)
        if obj!=None and permission and not self.validate_access(obj,permission):
            return None
        return obj

    def get_module(self,name,permission="",byname=False,exc=False):
        """
        Returns module presented in application by its name or alias depending on permissions (if given).
        if *exc* is True the exception will be raised if module was not found.
        """
        if byname:
            obj=self.app.module_manager.get_object_byname(name,exc)
        else:
            obj=self.app.module_manager.get_object_byalias(name,exc)
        if obj!=None and permission and not self.validate_access(obj,permission):
            return None
        return obj
                
    def devices(self,permission=""):
        """Returns a list of names of devices presented in application."""
        return [obj.name for _, obj in self.iterate_devices(permission)]
            
    def commands(self,permission=""):
        """Returns a list of names of commands presented in application."""
        return [obj.name for _, obj in self.iterate_commands(permission)]
    
    def modules(self,permission=""):
        """Returns a list of names of modules presented in application."""
        return [obj.name for _, obj in self.iterate_modules(permission)]
        
    def objects(self,permission=""):
        """Returns a list of names of devices, commands and modules presented in application."""
        return self.devices(permission)+self.commands(permission)+self.modules(permission)        

    def sysmods(self,permission=""):
        """Returns a list of names of system modules presented in application."""
        return [obj.name for _, obj in self.iterate_sysmods(permission)]

    def complete(self, text, line, begidx, endidx): 
        try:
            if begidx>0:
                line=line.strip()
                cmd=line.split()[0]
                if cmd:
                    obj=self.get_command(cmd,byname=True, exc=False)
                    if not obj: return []
                    else:
                        completion_matches = obj.call_complete(text, line)
                        return completion_matches
                return self.commands(permission="execute")
            return get_completions(text,self.commands(permission="execute"))
        except Exception:
            traceback.print_exc()
    
    def status(self):
        """Status handler for application module. By default it shows number of devices, commands and modules in application"""
        return (("Devices", len(self.app.device_manager), ""),
                ("Modules", len(self.app.module_manager), ""),
                ("Commands", len(self.app.module_manager), ""))    
        
    @property
    def projname(self):
        """Returns application name"""
        return self.app.projname
    
    @property
    def projpath(self):
        """Returns path to application"""
        return self.app.projpath
    
    @property
    def noauth(self):
        return self.auth_module.noauth
    
    