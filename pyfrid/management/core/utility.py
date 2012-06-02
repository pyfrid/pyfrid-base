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
    
