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


import os
import sys
import pyfrid

class RegistryError(Exception): pass

class ObjectRegistry(object):
    
    def __init__(self):
        self._class_registry={}
       
    def register(self,cls):
        pyfrid_dirs = [os.path.abspath(path_) for path_ in pyfrid.__path__]
        cls_dir = os.path.dirname(os.path.abspath(sys.modules[cls.__module__].__file__))
        if not any([cls_dir.startswith(path_) for path_ in pyfrid_dirs]):
            try:
                if not cls.alias:
                    raise RegistryError("Empty alias for class {0}".format(cls.__name__))
                if cls.alias in self._class_registry:
                    raise RegistryError("Duplicate alias for '{0}': second object '{1}'".format(
                                            cls.__name__,
                                            self._class_registry[cls.alias].__name__
                    ))
                self._class_registry[cls.alias]=cls
            except AttributeError:
                raise RegistryError("No alias  for class {0}".format(cls.__name__))
            
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
        
        