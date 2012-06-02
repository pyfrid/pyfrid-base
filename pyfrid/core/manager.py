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
#

import traceback
from pyfrid.utils.odict import odict

class ObjectManagerError(Exception): pass

class ObjectManager(object):
    
    def __init__(self):
        self._objects=odict()
        self._names=odict()
            
    def create_object(self, cls, app, config_permissions={}, config_settings={}):
        try:
            obj=cls(app, config_permissions=config_permissions, config_settings=config_settings)
        except Exception:
            raise ObjectManagerError("Exception while creating object with alias '{0}':\n {1}".format(cls.alias,traceback.format_exc()))
        if not obj.name: 
            raise ObjectManagerError("Object with alias '{0}': empty name".format(cls.alias))
        if obj.name in self._names:
            raise ObjectManagerError("Duplicate names for objects with aliases '{0}' and '{1}'".format(obj.alias,self._names[obj.name]))
        self._objects[cls.alias]=obj
        self._names[obj.name]=obj.alias
        return self._objects[obj.alias]
    
    def add_object(self,obj):
        if not obj.name: 
            raise ObjectManagerError("Object with alias '{0}' has empty name".format(obj.alias))
        if obj.name in self._names:
            raise ObjectManagerError("Duplicate names for objects with aliases '{0}' and '{1}'".format(obj.alias,self._names[obj.name]))
        self._objects[obj.alias]=obj
        self._names[obj.name]=obj.alias
        return self._objects[obj.alias]
    
    def get_object_byalias(self, alias, exc=False):
        obj=None
        try: 
            obj=self._objects[alias] 
        except KeyError:
            if exc: raise ObjectManagerError("Object  with alias '{0}' not found".format(alias))
            else: return None
        return obj
    
    def get_object_byname(self, name, exc=False):
        obj=None
        if name not in self._names:
            if exc: raise ObjectManagerError("Object  with name '{0}' not found".format(name))
            else: return None
        else: obj=self._objects[self._names[name]]
        return obj
            
    def iterate_objects(self, byname=False):
        if byname:
            for item in self._names:
                obj=self.get_object_byname(item, exc=False)
                if obj!=None: yield (item,obj)
        else:
            for item in self._objects:
                obj=self.get_object_byalias(item, exc=False)
                if obj!=None: yield (item,obj)
                
    def objects(self):
        return [name for name, _ in self.iterate_objects(byname=True)]

    
    def __len__(self):
        return len(self._objects)                

