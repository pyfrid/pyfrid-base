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