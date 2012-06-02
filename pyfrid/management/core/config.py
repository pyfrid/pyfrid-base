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

import os
from abc import ABCMeta, abstractmethod

from pyfrid.utils.odict import odict
from pyfrid.management.core.registry import BaseRegistry, RegistryError

class ConfigError(Exception): pass

class ConfigManagerRegistry(BaseRegistry): pass    

config_registry=ConfigManagerRegistry()
    
class ConfigManagerMeta(ABCMeta):
    
    def __init__(cls, name, bases, d):
        try:
            config_registry.register(cls)
        except RegistryError, err:
            raise RegistryError("Exception while registering class '{0}': {1}".format(cls.__class__.__name__,err))
        return ABCMeta.__init__(cls, name, bases, d)


class BaseConfigManager(object):

    __metaclass__=ConfigManagerMeta
    
    name=""
    
    extension=None

    def __init__(self, projpath, config_subfolder=""):
        self._projpath=projpath
        self._subfolder=config_subfolder
        self._system_config   = odict()
        self._modules_config  = odict()
        self._devices_config  = odict()
        self._commands_config = odict()
        try:
            self._mainfolder=os.path.join (self._projpath, "config")
            if not os.path.exists(self._mainfolder):  raise ConfigError("Main config folder doesn't exist")
            self._cfgcmdpath=os.path.join (self._mainfolder,"commands.{0}".format(self.extension))
            if not os.path.exists(self._cfgcmdpath):  raise ConfigError("Default config file '{0}' doesn't exist".format(self._cfgcmdpath))
            self._cfgdevpath=os.path.join (self._mainfolder,"devices.{0}".format(self.extension))
            if not os.path.exists(self._cfgdevpath):  raise ConfigError("Default config file '{0}' doesn't exist".format(self._cfgdevpath))
            self._cfgmodpath=os.path.join (self._mainfolder,"modules.{0}".format(self.extension))
            if not os.path.exists(self._cfgmodpath):  raise ConfigError("Default config file '{0}' doesn't exist".format(self._cfgmodpath))
            self._cfgsyspath=os.path.join (self._mainfolder,"system.{0}".format(self.extension))
            if not os.path.exists(self._cfgsyspath):  raise ConfigError("Default config file '{0}' doesn't exist".format(self._cfgsyspath))
            if self._subfolder:
                p=os.path.join (self._mainfolder,self._subfolder,"commands.{0}".format(self.extension))
                if os.path.exists(p): self._cfgcmdpath=p
                p=os.path.join (self._mainfolder,self._subfolder,"devices.{0}".format(self.extension))
                if os.path.exists(p): self._cfgdevpath=p
                p=os.path.join (self._mainfolder,self._subfolder,"modules.{0}".format(self.extension))
                if os.path.exists(p): self._cfgmodpath=p
                p=os.path.join (self._mainfolder,self._subfolder,"system.{0}".format(self.extension))
                if os.path.exists(p): self._cfgsyspath=p    
            self.load_config()
        except Exception, err:
            raise ConfigError(err)
        
    def _iterate_objects(self,cfg):
        for alias,item in cfg.iteritems():
            yield(alias,item["permissions"],item["settings"])
    
    def iterate_sysmod(self):
        return self._iterate_objects(self._system_config)
    
    def iterate_commands(self):
        return self._iterate_objects(self._commands_config)
        
    def iterate_devices(self):
        return self._iterate_objects(self._devices_config)
    
    def iterate_modules(self):
        return self._iterate_objects(self._modules_config)
    
    def get_module_config(self,alias,pop=False):
        try:
            if pop: cfg=self._modules_config.pop[alias]
            else: cfg=self._modules_config[alias]
            return cfg
        except IndexError:
            raise ConfigError("No module found with alias '{0}'".format(alias))
        
    def get_sysmod_config(self,alias,pop=False):
        try:
            if pop: cfg=self._system_config.pop[alias]
            else: cfg=self._system_config[alias]
            return cfg
        except IndexError:
            raise ConfigError("No system module found with alias '{0}'".format(alias))
    
    def get_device_config(self,alias,pop=False):
        try:
            if pop: cfg=self._devices_config.pop[alias]
            else: cfg=self._devices_config[alias]
            return cfg
        except IndexError:
            raise ConfigError("No device found with alias '{0}'".format(alias))
        
    def get_command_config(self,alias,pop=False):
        try:
            if pop: cfg=self._commands_config.pop[alias]
            else: cfg=self._commands_config[alias]
            return cfg
        except IndexError:
            raise ConfigError("No command found with alias '{0}'".format(alias))
    
    def load_config(self):
        try:
            self.load_system_config(self._cfgsyspath,self._system_config)
            self.load_devices_config(self._cfgdevpath,self._devices_config)
            self.load_commands_config(self._cfgcmdpath,self._commands_config)
            self.load_modules_config(self._cfgmodpath,self._modules_config)
        except Exception, err:
            raise ConfigError("Error while loading configuration: {0}".format(err))
        
    @abstractmethod
    def load_devices_config  (self, path, holder):
        pass
    
    @abstractmethod
    def load_commands_config (self, path, holder):
        pass
    
    @abstractmethod
    def load_modules_config  (self, path, holder):
        pass
    
    @abstractmethod
    def load_system_config   (self, path, holder):
        pass
    
    @abstractmethod
    def create_device_config(self, alias, name, active=True, settings={}, permissions={}):
        pass
    
    @abstractmethod
    def create_command_config(self, alias, name, active=True, settings={}, permissions={}):
        pass
    
    @abstractmethod
    def create_module_config(self, alias, name, active=True, settings={}, permissions={}):
        pass
        
        