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


from pyfrid.core import BaseThreadedCommand
from pyfrid.utils import format_value

class BaseReferenceCommand(BaseThreadedCommand):
    
    numthreads=4
            
    def call_each_execute(self, obj, *args, **kwargs):
        self.info("Referencing '{0}' ...".format(obj.name ))
        super(BaseReferenceCommand, self).call_each_execute(obj, *args,**kwargs)
        curpos=obj.call_position()
        self.info("Current position of {0}: {1} {2}".format(obj.name,format_value(curpos),obj.units))
         
    def grammar(self):
        from pyfrid.modules.system.vm.leplvm import DEVICE, CONSTVALUE
        return (DEVICE, 1, None)
    