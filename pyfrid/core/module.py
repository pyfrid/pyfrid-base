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
    """This is a base module class. Modules are used to make different kind of tasks and their functionality is not limited."""
    
    __metaclass__=ModuleMetaClass

    def __init__(self, app, *args, **kwargs):
        for _, descr in self.used_modules.iteritems():
            mod=app.get_module(descr.alias,exc=True)
            descr.object=mod
        for _, descr in self.used_devices.iteritems():
            dev=app.get_device(descr.alias,exc=True)
            descr.object=dev
        super(BaseModule,self).__init__(app, *args,**kwargs)
        