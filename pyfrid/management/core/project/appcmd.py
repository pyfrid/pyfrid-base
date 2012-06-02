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
import sys
import traceback
from optparse import make_option

import pyfrid
from pyfrid.management.core.config import config_registry
from pyfrid.management.core.command import CommandError
from pyfrid.management.core.project import BaseProjectCommand
from pyfrid.core.sysmod import system_registry
from pyfrid.core.manager import ObjectManager
from pyfrid.utils import splitall

class BaseApplicationCommand(BaseProjectCommand):
    
    appmodule_alias="application"
    
    option_list=[
        make_option("-c", "--config-subfolder", dest="config_subfolder", type="string", default="", help="Name of subfolder with configuration files"),
        make_option("-t", "--config-type", dest="config_type", type="string", default="yaml", help="Configuration manager type.")
    ]    
    
    def __init__(self, apppath):
        super(BaseApplicationCommand,self).__init__(apppath)
        self._system_manager=ObjectManager()
        self._device_manager=ObjectManager()
        self._command_manager=ObjectManager()
        self._module_manager=ObjectManager()
        self._config_manager=None
        self._appmod=None
    
    @property
    def appmod(self):
        if self._appmod==None:
            raise AttributeError, "application module has not been initialized yet"
        return self._appmod
    
    @property
    def config_manager(self):
        if self._config_manager==None:
            raise AttributeError, "configuration manager has not been initialized yet"
        return self._config_manager
    
    @property
    def system_manager(self):
        return self._system_manager
    
    @property
    def module_manager(self):
        return self._module_manager
    
    @property
    def command_manager(self):
        return self._command_manager
    
    @property
    def device_manager(self):
        return self._device_manager
            
    def import_path(self,path, exclude_path=True):
        path=os.path.abspath(path)
        start_index=len(path)
        sys.path.insert(0, path)
        try:
            for dirpath, _, filenames in os.walk(path):
                if exclude_path and dirpath==path: continue
                for f in filenames:
                    if f!= "__init__.py" and f.endswith(".py"):
                        dpath=dirpath[start_index:]
                        if not dpath: mod=f[:-3]
                        else:
                            mod="{0}.{1}".format(".".join(splitall(dpath)),f[:-3])
                        __import__(mod)
        except ImportError, err:
            traceback.print_exc()
            raise CommandError("Project import error: {0}".format(err))
        finally:
            del sys.path[0]
    
    def initialize(self, config_type, config_subfolder):
        self.import_path(os.path.join(pyfrid.__path__[0],"management","config"),exclude_path=False)
        self._config_manager=config_registry[config_type](self.projpath, config_subfolder)
        
        for alias, permissions, settings in self.config_manager.iterate_sysmod():
            self._system_manager.create_object(system_registry[alias], self, permissions, settings)
        
        self._appmod=self.system_manager.get_object_byalias(self.appmodule_alias, exc=True)
        
        for _, mod in self._system_manager.iterate_objects():
            mod.call_initialize()
                    
    def preloop(self, *args, **options):
        return True
    
    def postloop(self, *args, **options):
        pass
        
    def mainloop(self, *args, **options):
        pass    
            
    def handle(self, *args, **options):
        self.import_path(self.projpath)
        config_subfolder=options.get("config_subfolder","")
        config_type=options.get("config_type","yaml")
        self.initialize(config_type, config_subfolder)
        if self.preloop(*args, **options):
            self.mainloop(*args, **options)
            self.postloop(*args, **options)
            
