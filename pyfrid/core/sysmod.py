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

from pyfrid.core.descriptor import UsedModuleDescriptor
from pyfrid.core.object import BaseObject, ObjectMetaClass, set_descriptors
from pyfrid.core.registry import ObjectRegistry, RegistryError
from pyfrid.core.descriptor import use_module

system_registry=ObjectRegistry()
    
class SystemModuleMetaClass(ObjectMetaClass):
    
    def __new__(meta, name, bases, d):
        d["used_modules"]=set_descriptors("used_modules", UsedModuleDescriptor, bases, d)
        return ObjectMetaClass.__new__(meta, name, bases, d)
    
    def __init__(cls, name, bases, d):
        ObjectMetaClass.__init__(cls, name, bases, d)
        try: system_registry.register(cls)
        except RegistryError, err:
            raise RegistryError("Exception while registering class '{0}': {1}".format(cls.__class__.__name__,err))


class _BaseSystemModule(BaseObject):     
    __metaclass__=SystemModuleMetaClass
    used_modules={}
    
    def __init__(self, app, *args, **kwargs):
        for _, descr in self.used_modules.iteritems():
            mod=app.system_manager.get_object_byalias(descr.alias,exc=True)
            descr.object=mod
            
        super(_BaseSystemModule, self).__init__(app, *args,**kwargs)
            
    def do_status(self):
        return self.call_status()

class BaseSystemModule(_BaseSystemModule):     
        
    logger_module=use_module("logger")
    
    def __init__(self, app, *args, **kwargs):        
        super(BaseSystemModule, self).__init__(app, *args,**kwargs)
        
        self.debug_signal.connect(self.logger_module.debug_slot)
        self.info_signal.connect(self.logger_module.info_slot)
        self.warning_signal.connect(self.logger_module.warning_slot)
        self.error_signal.connect(self.logger_module.error_slot)
        self.exception_signal.connect(self.logger_module.exception_slot)
            