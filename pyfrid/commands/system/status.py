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


from lepl import Or
from pyfrid.core import BaseThreadedCommand
from pyfrid.utils import format_status

class BaseStatusCommand(BaseThreadedCommand):     
    numthreads=4
    
    def call_each_execute(self, obj, *args, **kwargs):
        status=super(BaseStatusCommand, self).call_each_execute(obj, *args, **kwargs)
        self.info("Current status of {0} {1}".format(obj.name,format_status(status,(30,15,5))))
        
    def grammar(self):
        from pyfrid.modules.system.vm.leplvm import OBJECT, SYSMOD
        return (Or(SYSMOD, OBJECT), 1, None)
    
    def completions(self):
        cpl=[obj.name for _,obj in self.app.iterate_objects(byname=True, permission=self.alias)]
        cpl.extend([obj.name for _,obj in self.app.iterate_sysmods(byname=True, permission=self.alias)])
        return ([cpl],True)