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
