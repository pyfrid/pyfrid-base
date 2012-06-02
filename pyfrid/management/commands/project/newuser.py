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