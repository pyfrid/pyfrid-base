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
#

import os
import sys
import traceback

import pyfrid
from pyfrid.management.core.admin   import admin_registry
from pyfrid.management.core.project import project_registry

from pyfrid.core.registry import RegistryError

class ManagementUtility(object):
            
    def __init__(self, argv, commands_path, registry):
        self.argv=argv
        self.prog_name = os.path.basename(self.argv[0])
        self.registry=registry
        sys.path.insert(0,commands_path)
        try:
            cmdlist=[f[:-3] for f in os.listdir(commands_path)
                if not f.startswith('.') and f!="__init__.py" and f.endswith('.py')]
            for cmd in cmdlist:
                __import__(cmd)
        except ImportError:
            sys.stderr.write("Error while importing module '{0}' from path {1}\n".format(cmd,commands_path))
            traceback.print_exc()
            sys.exit(1)
        except RegistryError:
            sys.stderr.write("Error while registering command from module '{0}' from path {1}\n".format(cmd,commands_path))
            sys.exit(1)
        finally:
            del sys.path[0]
            
    def print_help(self):
        """
        Returns the script's main help text, as a string.
        """
        usage = ['',"Type '{0} help <subcommand>' for help on a specific subcommand.".format(self.prog_name),'']
        usage.append('Available subcommands:')
        commands=self.registry.commands()
        commands.sort()
        for cmd in commands:
            usage.append('  {0}'.format(cmd))
        sys.stdout.write('\n'.join(usage)+'\n')
        
    def execute(self):
        apppath=os.path.abspath(self.argv[0])
        try: subcommand=self.argv[1]
        except IndexError: subcommand="help"
        if subcommand=="help":
            if len(self.argv)>2:
                klass=getattr(self.registry,self.argv[2],None)
                if klass==None: 
                    sys.stderr.write(" Unknown command '{0}'\n".format(self.argv[2]))
                    self.print_help()
                    return
                else: 
                    klass().print_help(self.prog_name)
                    return
            self.print_help()
            return
        klass=getattr(self.registry,subcommand,None)
        if klass==None: 
            sys.stderr.write(" Unknown command '{0}'\n".format(self.argv[2]))
            self.print_help()
            return 
        cmdobj =klass(apppath)
        arguments=self.argv[2:] if len(self.argv)>2 else []
        cmdobj(arguments)
                       
def execute_admin(argv):
    utility = ManagementUtility(argv,os.path.join(pyfrid.__path__[0],'management','commands','admin'),admin_registry)
    utility.execute()

def execute_manager(argv):
    utility = ManagementUtility(argv,os.path.join(pyfrid.__path__[0],'management','commands','project'),project_registry)
    utility.execute()
    
