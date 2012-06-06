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
from types import ListType

from pyfrid.utils.threadpool import ThreadPool
from pyfrid.core.signal import Signal
from pyfrid.core.descriptor import UsedDeviceDescriptor, UsedModuleDescriptor
from pyfrid.core.object import BaseProjectObject, ObjectMetaClass, set_descriptors
from pyfrid.core.registry import ObjectRegistry, RegistryError

command_registry=ObjectRegistry()

def get_completions(text, compbase):
    if type(compbase) != ListType:
        compbase=[compbase]
    if not text:
        completions = compbase[:]
    else:
        completions = [ f
        for f in compbase
            if f.startswith(text)
            ]
    return completions
    
class CommandMetaClass(ObjectMetaClass):
    
    def __new__(meta, name, bases, d):
        d["_used_devices"]=set_descriptors("_used_devices", UsedDeviceDescriptor, bases, d)
        d["_used_modules"]=set_descriptors("_used_modules", UsedModuleDescriptor, bases, d)
        return ObjectMetaClass.__new__(meta, name, bases, d)
    
    def __init__(cls, name, bases, d):
        ObjectMetaClass.__init__(cls, name, bases, d)
        try: command_registry.register(cls)
        except RegistryError, err:
            raise RegistryError("Exception while registering class '{0}': {1}".format(name,err))

class BaseCommand(BaseProjectObject):
    """This is a base class for all types of commands.
     Commands are used in PyFRID as an interaction interface between users and application.
     Any command can be linked to other devices and modules with *use_device* and *use_module* functions by their aliases
     """
    __metaclass__ = CommandMetaClass
    
    _used_devices={}
    _used_modules={}
        
    def __init__(self, app, *args, **kwargs):
        for _, descr in self._used_devices.iteritems():
            dev=app.device_manager.get_object_byalias(descr.alias, exc=True)
            descr.object=dev
        for _, descr in self._used_modules.iteritems():
            mod=app.get_module(descr.alias,exc=True)
            descr.object=mod
              
        super(BaseCommand,self).__init__(app, *args,**kwargs)
        
        self.before_execute_signal=Signal(self)
        self.after_execute_signal=Signal(self)
        self.before_validate_signal=Signal(self)
        self.after_validate_signal=Signal(self)
        self._busy=False
    
    @property
    def busy(self):
        """The property, which returns the value of *busy* flag"""
        return self._busy
        
    def call_execute(self, *args, **kwargs):
        """Caller for the *execute* handler. It keeps *busy* flag True value, while execution is performed"""
        self._busy=True
        try:
            return self.execute(*args,**kwargs)
        finally:
            self._busy=False
        
    def call_grammar(self,*args,**kwargs):
        """Caller for *grammar* handler"""
        return self.grammar()
    
    def call_runtime(self,*args,**kwargs):
        """Caller for *runtime* handler"""
        return float(self.runtime(*args, **kwargs))
    
    def call_validate(self,*args,**kwargs):
        """Caller for *runtime* handler"""
        return self.validate(*args,**kwargs)
    
    def call_complete(self, text, line):
        """
        Caller for *runtime* handler.
        Returns the completion list for the typed text
        """
        completions,repeat=self.completions()
        if not completions: return []
        l=len(line.split())-1
        if text and l>0: l-=1
        compl=[]
        cl=len(completions)
        if repeat: compl=completions[l-int(l/cl)*cl]
        else:
            try: compl=completions[l]
            except IndexError: return []
        return get_completions(text,compl)
    
    @abc.abstractmethod
    def execute(self, *args,**kwargs):
        """Abstract execution handler. Put here a code which must be run during the command execution"""
        pass
    
    @abc.abstractmethod
    def grammar(self):
        """Abstract grammar handler. It must return grammar rules which are understood by the *VirtualMachineModule*"""  
        return (None, None, None)

    def completions(self):
        """
        Returns completions for the current command as a tuple. The first item of the tuple is a list of lists with
        possible completions for every command parameter.
        The second item is a boolean flag which True value indicates that command parameters are repeatable.
        Example for the command like *command parameter1 parameter2*, where possible values of paramater1 are par11, par12 
        and possible values of parameter2 are par21, par22: 
        >>> return ([["par11", "par12"], ["par21","par22"]], False) 
        """
        return ([],False)
    
    @abc.abstractmethod          
    def validate(self,*args,**kwargs):
        """Abstract validate handler. It must return True or False after validating of values of the command parameters"""
        return True
    
    @abc.abstractmethod
    def runtime(self,*args,**kwargs):
        """Abstract runtime handler. It returns a calculated time of execution of the command"""
        return 0.0
    
    def status(self):
        """Standard status handler. It can be overwritten if needed"""
        return (("busy",self.busy,""),)

        
class BaseThreadedCommand(BaseCommand):
    """
    Base  command class for a command with multiple parameters, like:
    command object1 parameter1 object2 parameter2 ...
    By default its grammar rule accepts OBJECT and VALUE repeated from one to infinite number of times and can be overwritten if necessary.
    A threaded command expects that every object to which it is applied, has special function-agent *do_{command_alias}* which does the actual job.
    If the *numthreads* parameter of the class is >1 the execution of the command for every OBJECT will be performed
    parallel in threads. The validation, runtime and completions handlers are automatic. 
    """
    numthreads=1 #: number of threads used for the command execution
    
    def __init__(self, *args, **kwargs):
        super(BaseThreadedCommand,self).__init__(*args,**kwargs)
        self.before_each_execute_signal=Signal(self)
        self.after_each_execute_signal=Signal(self)
        self.numbaseargs=1
        gr, foo, _=self.grammar()
        if type(gr)==ListType:
            self.numbaseargs=len(gr)
            
    def completions(self):
        return ([[obj.name for _,obj in self.app.iterate_objects(byname=True, permission=self.alias) if obj.can(self.alias)]],True)
    
    def execute(self,*args,**kwargs):
        arguments=[args[i:i+self.numbaseargs] for i in range(0,len(args),self.numbaseargs)]
        pool=ThreadPool(self,self.numthreads, persist=False)
        for args_ in arguments:
            pool.add_task(self.call_each_execute, *args_) 
        pool.join_all()
    
    def call_each_execute(self, obj, *args, **kwargs):
        f=getattr(obj,"do_{0}".format(self.alias))
        return f(*args,**kwargs)
    
    def call_each_validate(self, obj, *args, **kwargs):
        if not obj.can(self.alias):
            self.error("no method '{0}' for object '{1}'".format(self.alias,obj.name))
            return False
        try:
            return getattr(obj,"validate_{0}".format(self.alias))(*args,**kwargs)
        except AttributeError:
            pass
        return True
    
    def call_each_runtime(self, obj, *args, **kwargs):
        try:
            return getattr(obj,"runtime_{0}".format(self.alias))(*args,**kwargs)
        except AttributeError:
            pass
        return 0.0
                
    def validate(self,*args, **kwargs):
        arguments=[(args[i],args[i+1:i+self.numbaseargs] if self.numbaseargs>1 else []) for i in range(0,len(args),self.numbaseargs)]
        res=[self.call_each_validate(arg[0],*arg[1]) for arg in arguments]
        return all(res)
    
    def runtime(self,*args):
        arguments=[(args[i],args[i+1:i+self.numbaseargs] if self.numbaseargs>1 else []) for i in range(0,len(args),self.numbaseargs)]
        res=[self.call_each_runtime(arg[0],*arg[1]) for arg in arguments]
        return max(res)
    
    def grammar(self):
        from pyfrid.modules.system.vm.leplvm import OBJECT
        return (OBJECT, 1, None)
    