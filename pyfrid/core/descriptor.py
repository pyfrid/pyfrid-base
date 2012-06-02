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


class BaseDescriptor(object):
    """
    Main class for all settings
    """
    _counter=0
    
    def __init__(self):
        self.counter_num=self._counter
        BaseDescriptor._counter+=1


class BaseObjectDescriptor(BaseDescriptor):
    
    def __init__(self, alias, obj=None):
        super(BaseObjectDescriptor, self).__init__()
        self._alias=alias
        self._object=obj
    
    @property
    def object(self):
        return self._object
    
    @object.setter
    def object(self,obj):
        self._object=obj
        
    @property
    def alias(self):
        return self._alias
        
    def __get__(self, instance, insttype=None):
        if self._object==None:
            raise AttributeError, "object is None"
        return self._object

    def __set__(self, instance, val):
        raise AttributeError, "can't set module descriptor"
    
    
    
class UsedModuleDescriptor(BaseObjectDescriptor):
    pass

def _use_object(alias, descriptor):
    #if type(alias)==ListType:
    #     return [descriptor(item) for item in alias]
    return descriptor(alias)

def use_module(alias):
    return _use_object(alias, UsedModuleDescriptor)

class UsedDeviceDescriptor(BaseObjectDescriptor):
    pass

def use_device(alias):
    return _use_object(alias, UsedDeviceDescriptor)

class UsedCommandDescriptor(BaseObjectDescriptor):
    pass

def use_command(alias):
    return _use_object(alias, UsedCommandDescriptor)

