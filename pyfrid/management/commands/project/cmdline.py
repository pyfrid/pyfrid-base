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

import os,sys
import string
import readline
import time
import getpass

from pyfrid.management.core.project.appcmd import BaseApplicationCommand

class CmdToolApplicationCommand(BaseApplicationCommand):            
    """Command line tool class""" 
    
    name='cmdline'
    descr = "Starts the command line tool"
    args = ""
    
    identchars = string.ascii_letters + string.digits + '_'
    intro=""
    
    def __init__(self, apppath):
        super(CmdToolApplicationCommand,self).__init__(apppath)
        self._auth=("","")
    
    def rawlines(self,prompt, lineprompt='...'):
        inp = []
        line =None
        while not line:
            line=raw_input(prompt)
        while line [-1]=='\\':
            inp.append(line[0:-1])
            line=raw_input(lineprompt)
            if not line:
                line+=chr(10)
        inp.append(line)
        return '\n'.join(inp)

    def login(self):
        if not self.appmod.noauth:
            try:
                while True:
                    login=raw_input("Login: ")
                    password=getpass.getpass("Password: ")
                    if self.appmod.login(login,password):
                        self._auth=(login,password)
                        return True
                    sys.stderr.write("Authentication failed. Wrong login or password\n")
            except KeyboardInterrupt:
                return False
        return True
            
    def logout(self):
        if not self.appmod.noauth:
            self.appmod.logout(*self._auth)

    def mainloop(self,*args, **options):
        prompt="{0}> ".format(self.projname) 
        try:
            if not self.login(): return False
            while True:
                try:
                    text = self.rawlines(prompt)
                    self.appmod.execute_code(text)
                    time.sleep(1.0)
                    while self.appmod.busy:
                        time.sleep(0.1)
                    time.sleep(0.5)
                except KeyboardInterrupt:
                    self.appmod.call_stop()
                    self.logout()
                    self.login ()
        except EOFError:
            pass           

    def preloop(self, *args, **options):
        history_file=os.path.join(os.getcwd(),".history")
        readline.set_completer_delims(string.whitespace+';')
        readline.set_completer(self.complete)
        readline.parse_and_bind("tab: complete")
        readline.set_history_length(100)
        if os.path.exists(history_file):
            readline.read_history_file(history_file)
        return True 
            
    def postloop(self, *args, **options):
        """Hook method executed once when the cmd_loop() method is about to
        return.
        """
        self.appmod.call_shutdown()

    def complete(self, text, state):
        """Return the next possible completion for 'text'.

        If a command has not been entered, then complete against command list.
        Otherwise try to call complete_<command> to get list of completions.
        """
#        
        if state == 0:
            origline = readline.get_line_buffer()
            lines=origline.split(';')
            lastline=lines[len(lines)-1]
            line = lastline.lstrip()
            stripped = len(lastline) - len(line)
            startidx=len(origline)-len(lastline)+1
            begidx = readline.get_begidx() -startidx -stripped
            endidx = readline.get_endidx() -startidx -stripped
            self.completion_matches=self.appmod.complete(text,line,begidx,endidx)
        try:
            return self.completion_matches[state]
        except IndexError:
            return None
        