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

from pyfrid.modules.system.vm.core.vm import ParseError
from pyfrid.modules.system.vm.leplvm import CmdStmtNode 
from pyfrid.core.command import BaseCommand
from pyfrid.core.settings import StringSetting

class MacroCmdStmtNode(CmdStmtNode):

    def process(self):
        super(MacroCmdStmtNode,self).process()
        cmd=self.pop(0)
        for i in range(0,len(self)):
            path=os.path.abspath(os.path.join(cmd.macropath,self[i]))
            code=''
            try:
                fd=open(path,"r")
                code=fd.read()
                fd.close()
            except IOError, err:
                raise ParseError("Exception while opening macro {0}".format(err))
            self[i]=(self.parser.parse_code(code), self[i])
        return self
    
    def validate(self):
        for ast, name in self:
            self.parser._current_macro=name
            if self.stop_flag: break
            for item in ast:
                if self.stop_flag: break
                if not item.validate(): return False
        return True
    
    def runtime(self):
        res=[]
        for ast, _ in self:
            res.extend([item.runtime() for item in ast])
        return sum(res)
            
    def execute(self):
        for ast, name in self:
            self.parser._current_macro=name
            if self.stop_flag: break
            for item in ast:
                if self.stop_flag: break
                item.execute()
        
    
class BaseMacroCommand(BaseCommand):

    node_type=MacroCmdStmtNode
    
    def __init__(self,*args,**kwargs):
        super(BaseMacroCommand, self).__init__(*args, **kwargs)
        self._macropath=self.macrodir
        
        self.app.auth_module.after_login_signal.connect(self.on_auth_slot)
        self.app.auth_module.after_logout_signal.connect(self.on_auth_slot)
    
    @property
    def macropath(self):
        return self._macropath
        
    def on_auth_slot(self, user, **kwargs):
        if user==None: 
            self._macropath=self.macrodir
            return
        path=os.path.join(self.macrodir,user.login)
        try:
            if not os.path.exists(path):
                os.makedirs(path)
        except OSError, err:
            self.error(err)
        else:
            self._macropath=path
    
    def setmaindir(self, directory):
        macrodir=os.path.abspath(directory)
        try:
            if not os.path.exists(macrodir):
                os.makedirs(macrodir)
        except OSError, err:
            self.error(err)
            self._macropath=self.macrodir
            return self.macrodir
        self._macropath=macrodir 
        return macrodir
                
    def grammar(self):
        from pyfrid.modules.system.vm.leplvm import STRCONST
        return (STRCONST,1,None)
    
    def execute(self,*args, **kwargs):
        pass 
    
    def runtime(self, *args, **kwargs):
        return 0.0
    
    def validate(self, *args, **kwargs):
        return True
                       
    macrodir=StringSetting("./macro", fixed=True, setter=setmaindir)
    