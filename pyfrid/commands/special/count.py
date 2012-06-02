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

from pyfrid.utils import format_value
from pyfrid.core import BaseThreadedCommand
        

class BaseCountCommand(BaseThreadedCommand):
    
    numthreads=4
            
    def call_each_execute(self, obj, tm, *args, **kwargs):
        self.info("Counting for '{0}' sec".format(tm))
        res=super(BaseCountCommand,self).call_each_execute(obj, tm,*args,**kwargs)
        self.info("Counting result: {0} {1}".format(obj.name,format_value(res),obj.units))
         
    def grammar(self):
        from pyfrid.modules.system.vm.leplvm import DEVICE, CONSTVALUE
        return ([DEVICE, CONSTVALUE], 1, None)
    