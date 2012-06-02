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

class RegistryError(Exception): pass

class BaseRegistry(object):
    
    def __init__(self):
        self._class_registry={}
        
    def register(self,cls):
        try:
            if not cls.name: return
            if cls.name in self._class_registry:
                raise RegistryError("Duplicate name for '{0}': second object '{1}'".format(
                                        cls.__class__.__name__,
                                        self._class_registry[cls.alias].__class__.__name__
                ))
            self._class_registry[cls.name]=cls
        except AttributeError:
            raise RegistryError("No name  for class {0}".format(cls.__class__.__name__))
        
    def __getattr__(self,name):
        if name in self._class_registry:
            return self._class_registry[name]
        else:
            raise RegistryError("No object named '{0}' in registry".format(name))
        
    def __getitem__(self,name):
        try:
            return self._class_registry[name]
        except KeyError:
            raise RegistryError("No object named '{0}' in registry".format(name))
        
class CommandRegistry(BaseRegistry):
    
    def commands(self):
        return self._class_registry.keys()