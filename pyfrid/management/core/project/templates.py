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

from string import Template

COMMANDCONFIGTEMPLATE=Template(
"""
---
#configuration for command $name
alias: $alias     
active: True   
name: $name 
permissions:
    view:    []
    execute: []
"""                      
)

DEVICECONFIGTEMPLATE=Template(
"""
---
#configuration for device $name
alias: $alias     
active: True   
name: $name 
permissions:
    view:    []
"""                      
)

MODULECONFIGTEMPLATE=Template(
"""
---
#configuration for module $name
alias: $alias     
active: True   
name: $name 
permissions:
    view:    []
"""                      
)

COMMANDTEMPLATE=Template(
"""
from $basemodule import $baseclass

class $objclass($baseclass):

    alias="$alias"
    
    descr="Type here a description..."
    
    def grammar(self):
        return super($objclass,self).grammar()
        
    def execute(self,*args,**kwargs):
        return super($objclass,self).execute(*args,**kwargs)
        
    def validate(self,*args,**kwargs):
        return super($objclass,self).validate(*args,**kwargs)
        
    def runtime(self,*args,**kwargs):
        return super($objclass,self).runtime(*args,**kwargs)
        
"""                      
)

DEVICETEMPLATE=Template(
"""
from $basemodule import $baseclass

class $objclass($baseclass):

    alias="$alias"
    
    descr="Type here a description..."
    
    def position(self):
        return super($objclass,self).position()
        
    def status(self):
        return super($objclass,self).status()
    
"""                      
)

MODULETEMPLATE=Template(
"""
from $basemodule import $baseclass

class $objclass($baseclass):

    alias="$alias"
    
    descr="Type here a description..."
    
    def status(self):
        return super($objclass,self).status()
            
"""                      
)
