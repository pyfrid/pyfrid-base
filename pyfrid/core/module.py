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

from pyfrid.core.descriptor import UsedModuleDescriptor, UsedDeviceDescriptor
from pyfrid.core.object import BaseProjectObject, ObjectMetaClass, set_descriptors
from pyfrid.core.registry import RegistryError, ObjectRegistry

module_registry=ObjectRegistry()

class ModuleMetaClass(ObjectMetaClass):
    
    def __new__(meta, name, bases, d):
        d["used_modules"]=set_descriptors("used_modules", UsedModuleDescriptor, bases, d)
        d["used_devices"]=set_descriptors("used_devices", UsedDeviceDescriptor, bases, d)
        return ObjectMetaClass.__new__(meta, name, bases, d)
    
    def __init__(cls, name, bases, d):
        ObjectMetaClass.__init__(cls, name, bases, d)
        try: module_registry.register(cls)
        except RegistryError, err:
            raise RegistryError("Exception while registering class '{0}': {1}".format(cls.__class__.__name__,err))
        
class BaseModule(BaseProjectObject):
    __metaclass__=ModuleMetaClass

    def __init__(self, app, *args, **kwargs):
        for _, descr in self.used_modules.iteritems():
            mod=app.get_module(descr.alias,exc=True)
            descr.object=mod
        for _, descr in self.used_devices.iteritems():
            dev=app.get_device(descr.alias,exc=True)
            descr.object=dev
        super(BaseModule,self).__init__(app, *args,**kwargs)
        