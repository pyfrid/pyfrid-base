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

