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