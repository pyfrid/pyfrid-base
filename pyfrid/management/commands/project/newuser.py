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
from optparse import make_option

import pyfrid
from pyfrid.management.core.config import config_registry
from pyfrid.management.core.command import CommandError
from pyfrid.management.core.project.appcmd import BaseApplicationCommand
from pyfrid.core.sysmod import system_registry

class NewUserCommand(BaseApplicationCommand):
    
    name='newuser'
    
    descr = "Creates a new user..."
    args = "[login]"
    
    option_list=[
        make_option("-c", "--config-subfolder", dest="config_subfolder", type="string", default="", help="Name of subfolder with configuration files"),
        make_option("-t", "--config-type", dest="config_type", type="string", default="yaml", help="Configuration manager type."),
    ]    
    
    def initialize(self, config_type, config_subfolder):
        self.import_path(os.path.join(pyfrid.__path__[0],"management","config"),exclude_path=False)
        self._config_manager=config_registry[config_type](self.projpath, config_subfolder)
        for alias, permissions, settings in self.config_manager.iterate_sysmod():
            self._system_manager.create_object(system_registry[alias], self, permissions, settings)
        self._appmod=self.system_manager.get_object_byalias(self.appmodule_alias, exc=True)
        self._appmod.auth_module.call_initialize()
        
                                
    def handle(self, login, **options):
        self.import_path(self.projpath)
        config_subfolder=options.get("config_subfolder","")
        config_type=options.get("config_type","yaml")
        self.initialize(config_type, config_subfolder)
        if self.appmod.auth_module.user_exists(login):
            raise CommandError("User '{0}' exists")
        import getpass
        pass1=getpass.getpass("Password: ")
        pass2=getpass.getpass("Retype password: ")
        if pass1!=pass2: raise CommandError("Passwords mismatch")
        groups=["USER"]
        _groups=raw_input("Comma separated groups to which user belongs [USER]:")
        if _groups.strip(): groups=[gr.strip() for gr in _groups.split(",")]
        name=raw_input("Name of the user: ")
        org=raw_input("Organization: ")
        email=raw_input("User email: ")
        self.appmod.auth_module.add_user(login, pass1, groups, name, org, email)