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

import sys
import os
import traceback
from optparse import OptionParser


class CommandError(Exception):
    """
    Exception class indicating a problem while executing a management
    command.

    If this exception is raised during the execution of a management
    command, it will be caught and turned into a nicely-printed error
    message to the appropriate output stream (i.e., stderr); as a
    result, raising this exception (with a sensible description of the
    error) is the preferred way to indicate that something has gone
    wrong in the execution of a command.

    """
    pass

        
class BaseCommand(object):
    
    descr = ''
    args = ''
    name=''
    
    option_list = []
    
    def __init__(self, apppath):
        self._projpath=apppath
        self._projname=os.path.basename(apppath)
    
    @property
    def projpath(self):
        return self._projpath
    
    @property
    def projname(self):
        return self._projname
        
    def usage(self):
        """
        Return a brief description of how to use this command, by
        default from the attribute ``self.descr``.
        """
        usage = "%%prog {0} [options] {1}".format(self.name, self.args)
        if self.descr: return "Usage: {0}\n\nDescription: {1}" .format(usage, self.descr)
        else: return usage

    def create_parser(self, prog_name):
        """
        Create and return the ``OptionParser`` which will be used to
        parse the arguments to this command.

        """
        return OptionParser(prog=prog_name,
                            usage=self.usage(),
                            option_list=self.option_list)

    def print_help(self, prog_name):
        """
        Print the help message for this command, derived from
        ``self.usage()``.

        """
        parser = self.create_parser(prog_name)
        parser.print_help()

    def __call__(self, arguments):
        parser = self.create_parser(self.projname)
        options, args = parser.parse_args(arguments)
        self.execute(*args, **options.__dict__)

    def execute(self, *args, **options):
        try:
            stdout = options.get('stdout', sys.stdout)
            stderr = options.get('stderr', sys.stderr)
            output = self.handle(*args, **options)
            if output: stdout.write("{0}\n".format(output))
        except CommandError, e:
            stderr.write("{0}\n".format(str(e)))
            sys.exit(1)
        except Exception, err:
            stderr.write("{0}\n".format(str(err)))
            traceback.print_exc()
            sys.exit(1)
            
    def handle(self, *args, **options):
        """
        The actual logic of the command. Subclasses must implement
        this method.
        """
        pass
    

    