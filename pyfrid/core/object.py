#    This file is part of PyFRID.
#
#    PyFRID is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    PyFRID is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with PyFRID.  If not, see <http://www.gnu.org/licenses/>.
#

import abc
from types import FunctionType, DictType
from threading import Lock
from contextlib import contextmanager
from pyfrid.core.settings import BaseSetting, StringSetting, SettingError
from pyfrid.core.signal import Signal
from pyfrid.utils.odict import odict

@contextmanager
def method_ctxmgr(obj, signal_suffix, locked, *args, **kwargs):
    _bs=getattr(obj, "before_{0}_signal".format(signal_suffix), None)
    _as=getattr(obj, "after_{0}_signal".format(signal_suffix), None)
    if locked: obj.lock()
    try:
        if _bs!=None: _bs(*args, **kwargs)
        yield
    except Exception, err:
        obj.exception(err)
    finally:
        if _as!=None: _as(*args, **kwargs)
        if locked: obj.unlock()
        

class method_decorator(object):

    def __init__(self, signal_suffix, locked):
        self._suffix=signal_suffix
        self._locked=locked

    def __call__(self, func):
        def wrapper(obj, *args, **kwargs):
            val=None
            with method_ctxmgr(obj, self._suffix, self._locked, *args, **kwargs):
                try:
                    val=func(obj, *args, **kwargs)
                except Exception, err:
                    obj.exception(err)
            return val
        return wrapper

def set_descriptors(container_name, descr_klass, bases, class_dict):
    temp=[]
    for attrname, attr in class_dict.items():
        if isinstance(attr,descr_klass):
            temp.append((attrname,attr))   
    temp.sort(key=lambda x: x[1].counter_num)
    for base in bases[::-1]:
        if hasattr(base, container_name):
            if hasattr(base, container_name):
                base_container=getattr(base,container_name).copy()
                for name,_ in temp:
                    if name in base_container:
                        del base_container[name]
                temp = base_container.items() + temp
    temp=odict(temp)
    return temp

class ObjectMetaClass(abc.ABCMeta):
        
    def __new__(meta, name, bases, d):
        new_dict = {}
        for attrname, attr in d.items():
            if type(attr) == FunctionType and attrname.startswith("do_"):
                attr = method_decorator(attrname[3:],True)(attr)
            if type(attr) == FunctionType and attrname.startswith("call_"):
                attr = method_decorator(attrname[5:],False)(attr)
            new_dict[attrname]=attr    
        new_dict["_settings"]=set_descriptors("_settings", BaseSetting, bases, d)
        return abc.ABCMeta.__new__(meta, name, bases, new_dict)
    
class BaseObject(object):
    """
    Base class for commands, modules and devices. Every object in PyFRID has alias and name.
    Alias is an internal unique name of an object used by PyFRID for identification and internal linking between objects.
    Name of an object is a string setting, it can be changed by a user in the configuration file. 
    """
    __metaclass__=ObjectMetaClass
    _settings={}
    
    alias=""
    name  = StringSetting("", fixed = True)
    group = StringSetting("", fixed = True)
        
    def __init__(self, appobj, config_permissions={}, config_settings={}):
        """
        Input parameters are: 
        appobj - reference to a parent of the object, config_permissions - dictionary with a user permissions,
        config_settings - dictionary with settings, their permissions and default values. 
        config_permissions and config_settings are defined in the configuration file  
        """
        #simple type check
        assert type(config_permissions)==DictType, "expect dictionary type for the config_permisiions parameter"
        assert type(config_settings)==DictType, "expect dictionary type for the config_settings parameter"
        
        self._appobj=appobj
        self._config_permissions=config_permissions
        self._config_settings=config_settings
        
        self._has_error=False
        self._has_exception=False
        self._has_info=False
        self._has_warning=False
        self._stop_flag=False
        
        self._lock=Lock()
        self._locked=False
        
        ##################signals###########################
        self.before_stop_signal=Signal(self)
        self.after_stop_signal=Signal(self)
        
        self.before_shutdown_signal=Signal(self)
        self.after_shutdown_signal=Signal(self)
        
        self.before_init_signal=Signal(self)
        self.after_init_signal=Signal(self)
        
        self.before_release_signal=Signal(self)
        self.after_release_signal=Signal(self)
        
        
        self.debug_signal=Signal(self)
        self.info_signal=Signal(self)
        self.warning_signal=Signal(self)
        self.error_signal=Signal(self)
        self.exception_signal=Signal(self)
        
        #initializing attributes of settings
        for attrname, attr in self._settings.iteritems():
            try:
                try:
                    cfg=self._config_settings[attrname]
                except KeyError:
                    attr.configure(self)
                else:
                    if type(cfg)==DictType: #if dict type then read permissions and value
                        value=cfg.pop("value",None)
                        perm=cfg.pop("permissions",None)
                        if cfg:
                            self.warning("Unknown setting parameters {0}: {1}, expect 'value' and 'permissions'".format(attrname, ", ".join(cfg.keys())))
                        attr.configure(self, default_value=value, permissions=perm)
                    else:#setting has only value
                        attr.configure(self,default_value=cfg)
                attr.initialize(self)
            except SettingError, err:
                raise SettingError("Setting {0} of {1} raised exception: {2}: ".format(attrname, self.alias, err) )
    
    @property
    def app(self):
        "Returns a reference to the parent"
        return self._appobj
                            
    @property
    def locked(self):
        """ """
        return self._locked
    
    @property
    def has_error(self):
        """ """
        return self._has_error
    
    @property
    def has_exception(self):
        """ """
        return self._has_exception
    
    @property
    def has_warning(self):
        """ """
        return self._has_warning
    
    @property
    def has_info(self):
        """ """
        return self._has_info
    
    @property
    def stopped(self):
        """ """
        return self._stop_flag
    
    def debug(self,mesg):
        """Emits a debug message"""
        self.debug_signal(mesg)
    
    def info(self,mesg):
        """Emits a normal information message"""
        self._has_info=True
        self.info_signal(mesg)

    def error(self,mesg):
        """Emits an error message"""
        self._has_error=True
        self.error_signal(mesg)
        
    def exception(self,mesg):
        """
        Emits an exception message.
        This function must be executed only with exception handler, when a traceback information exists
        """
        self._has_exception=True
        self.exception_signal(mesg)
            
    def warning(self,mesg):
        """Emits a warning message"""
        self._has_warning=True
        self.warning_signal(mesg)

    def iterate_settings(self,fixed=None):
        """A generator which yields settings of an object. if fixed is None returns all settings."""
        if fixed!=None:
            for sname, sobj in self._settings.iteritems():
                if sobj.fixed==fixed:
                    yield (sname,sobj)
        else:
            for sname, sobj in self._settings.iteritems():
                yield (sname,sobj)
            
    def validate_setting(self, name, value=None, check_value=True):
        """
        This function is useful if setting is changed during runtime.
        It will check if setting with a name *name* exists and depending on *check_value* parameter will also validate its value.
        """ 
        if not self._settings.has_key(name):
            self.error(" no setting named '{0}.{1}'".format(self.name, name))
            return False 
        if check_value:
            if self._settings[name].fixed:
                self.error("setting '{0}' is fixed".format(name))
                return False
            try:
                self._settings[name].validate(value)
            except SettingError, err:
                self.error(err)
                return False
        return True
            
    def call_initialize(self):
        """Caller for the initialization handler. This function calls *release* handler, 
        initializes settings to their default values and calls *initialize* handler of the object"""
        self.info("Initialization...")
        self.call_release()
        self._has_exception=False
        for sname,sobj in self.iterate_settings(fixed=False):
            try:
                sobj.initialize(self)
            except SettingError, err:
                self.exception("Setting error raised by {0}.{1}: {2}".format(self.alias, sname, err))
        self.initialize()
    
    def call_release(self):
        """Caller for the release handler. This function releases flags, unlocks the object if it remained locked for any reason,
        and calls *release* handler of the object. The *release* handler is normally called before a command execution.
        It is better to avoid any long running routines inside the *release* handler. 
        """
        self._has_error=False
        self._has_warning=False
        self._has_info=False
        self._stop_flag=False
        self.unlock()
        self.release()  
    
    def call_status(self):
        """Caller for a *status* handler"""
        s_=self.status()
        s=tuple(s_ if s_!=None else [])
        return s
    
    def call_stop(self):
        """Caller for a *stop* handler"""
        self._stop_flag=True
        self.stop()
            
    def call_shutdown(self):
        """Caller for the *shutdown* handler. It is normally needed if your device must be shutdown properly, before the program will exit"""
        self.info("Shutdown ...".format(self.name))
        self.call_stop()
        self.shutdown()
    
    def lock(self):
        """Locks this object.
           While the object is locked and function acquires a new locking, the object will be blocked.
           This is useful for devices. For example during moving the device no further moving operation can be done.
        """
        try:
            if self._locked:
                self.warning("{0} is locked. Waiting for unlocking...".format(self.name))
            self._lock.acquire() 
        except:
            pass
        else:
            self._locked=True
          
    def unlock(self):
        """Releases the lock of the object"""
        try: 
            self._lock.release()
        except:
            pass
        else:
            self._locked=False
    
    def get_permission_groups(self,permname):
        """
        Returns a list of permission groups (usergroups) for the permission. Permission is normally
        an alias of an action which corresponds to an alias of a command or any other special name related to the object.
         """
        return self._config_permissions.get(permname,[])
    
    def can(self,method):
        """Checks if a command with alias *method* can be performed by the object"""
        if method and hasattr(self,"do_{0}".format(method)):
            return True
        return False
    
    def __str__(self):
        return self.name
                              
    def stop(self):
        """Stop handler. Put here the code which must be run to stop the object."""
        pass
    
    def release(self):
        """Release handler. Put here the code which must be run to release the object."""
        pass
    
    def initialize(self):
        """Initialize handler. Put here the code which must be run to initialize the object."""
        pass
    
    def shutdown(self):
        """Shutdown handler"""
        pass
    
    def status(self):
        """Status handler"""
        pass


    
class BaseProjectObject(BaseObject):
    
    """This is a base class for the commands, devices and normal modules. 
    It overwrites several functions of the *BaseObject* class, adding access control and implying that 
    the parent of the object is an *BaseApplicationModule* system module"""
    
    def __init__(self, app, *args, **kwargs):
        super(BaseProjectObject, self).__init__(app, *args,**kwargs)
    
    def iterate_settings(self, permission="", fixed=False):
        """Yields settings depending on the permission of the current logged in user and *fixed* flag"""
        if permission:
            for name, sobj in super(BaseProjectObject, self).iterate_settings(fixed=fixed):
                if self.validate_setting(name, permission=permission, check_value=False):
                    yield(name, sobj)
        else:
            for name, obj in super(BaseProjectObject, self).iterate_settings(fixed=fixed):
                yield(name, obj)
           
    def settings(self, permission=""):
        """This function returns a list of all settings, which are configurable by a user and
        have proper permissions""" 
        return [name for name, _ in self.iterate_settings(permission, fixed=False)]
        
    def validate_setting(self, name, value=None, permission="", check_value=True):
        """It is the same function as in *BaseObject* class, but with *permission* control"""
        if super(BaseProjectObject, self).validate_setting(name, value=value, check_value=check_value):   
            if permission:
                sobj=self._settings[name]
                def perm_getter(permission):
                    return sobj.get_permission_groups(self, permission)
                if not self.app.validate_access(perm_getter, permission=permission):
                    self.error("Access denied to setting '{0}'".format(name))
                    return False
            return True
        return False
    
    def do_initialize(self):
        """Agent for the *BaseInitCommand*"""
        return self.call_initialize()
    
    def do_stop(self):
        """Agent for the *BaseStopCommand*"""
        return self.call_stop()
    
    def do_status(self):
        """Agent for the *BaseStatusCommand*"""
        return self.call_status()
    
        